import asyncio
import logging
import sys
from collections import defaultdict

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, NextStep, Achievement
from galaxy.api.consts import Platform
from galaxy.api.jsonrpc import InvalidParams
from galaxy.api.errors import ApplicationError, InvalidCredentials, UnknownError, AuthenticationRequired
from cache import Cache
from http_client import AuthenticatedHttpClient
from psn_client import (
    CommunicationId, TitleId, TrophyTitles, UnixTimestamp,
    PSNClient, MAX_TITLE_IDS_PER_REQUEST
)
from typing import Dict, List, Set, Iterable, Tuple, Optional
from version import __version__

from http_client import OAUTH_LOGIN_URL, OAUTH_LOGIN_REDIRECT_URL

AUTH_PARAMS = {
    "window_title": "Login to My PlayStation\u2122",
    "window_width": 536,
    "window_height": 675,
    "start_uri": OAUTH_LOGIN_URL,
    "end_uri_regex": "^" + OAUTH_LOGIN_REDIRECT_URL + ".*"
}

_CID_TIDS_DICT = Dict[TitleId, Set[CommunicationId]]
_TID_CIDS_DICT = Dict[CommunicationId, Set[TitleId]]
_TID_TROPHIES_DICT = Dict[TitleId, List[Achievement]]

class PSNPlugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.Psn, __version__, reader, writer, token)
        self._http_client = AuthenticatedHttpClient(self.lost_authentication)
        self._psn_client = PSNClient(self._http_client)
        self._comm_ids_cache: Dict[TitleId, List[CommunicationId]] = {}
        self._trophies_cache = Cache()
        logging.getLogger("urllib3").setLevel(logging.FATAL)

    async def _do_auth(self, npsso):
        if not npsso:
            raise InvalidCredentials()

        await self._http_client.authenticate(npsso)
        user_id, user_name = await self._psn_client.async_get_own_user_info()

        return Authentication(user_id=user_id, user_name=user_name)

    async def authenticate(self, stored_credentials=None):
        stored_npsso = stored_credentials.get("npsso") if stored_credentials else None
        if not stored_npsso:
            return NextStep("web_session", AUTH_PARAMS)

        return await self._do_auth(stored_npsso)

    async def pass_login_credentials(self, step, credentials, cookies):
        def get_npsso():
            for c in cookies:
                if c["name"] == "npsso" and c["value"]:
                    return c["value"]

        npsso = get_npsso()
        auth_info = await self._do_auth(npsso)
        self.store_credentials({"npsso": npsso})
        return auth_info

    @staticmethod
    def _is_game(comm_id: List[CommunicationId]) -> bool:
        """Assumption: all games has communication id - otherwise it's DLC"""
        return comm_id != []

    async def update_communication_id_cache(self, title_ids: List[TitleId]) \
            -> Dict[TitleId, List[CommunicationId]]:
        async def updater(title_id_slice: Iterable[TitleId]):
            delta.update(await self._psn_client.async_get_game_communication_id_map(title_id_slice))

        delta: Dict[TitleId, List[CommunicationId]] = dict()
        await asyncio.gather(*[
            updater(title_ids[it:it + MAX_TITLE_IDS_PER_REQUEST])
            for it in range(0, len(title_ids), MAX_TITLE_IDS_PER_REQUEST)
        ])

        self._comm_ids_cache.update(delta)
        return delta

    async def get_game_communication_ids(self, title_ids: List[TitleId]) -> Dict[TitleId, List[CommunicationId]]:
        result: Dict[TitleId, List[CommunicationId]] = dict()
        misses: Set[TitleId] = set()
        for title_id in title_ids:
            comm_ids: Optional[List[CommunicationId]] = self._comm_ids_cache.get(title_id)
            if comm_ids is not None:
                result[title_id] = comm_ids
            else:
                misses.add(title_id)

        if misses:
            result.update(await self.update_communication_id_cache(list(misses)))

        return result

    async def get_owned_games(self):
        async def filter_games(titles):
            comm_id_map = await self.get_game_communication_ids([t.game_id for t in titles])
            return [title for title in titles if self._is_game(comm_id_map[title.game_id])]

        return await filter_games(
            await self._psn_client.async_get_owned_games()
        )

    # TODO: backward compatibility. remove when GLX handles batch imports
    async def get_unlocked_achievements(self, game_id: TitleId):
        async def get_game_comm_id():
            comm_ids: List[CommunicationId] = (await self.get_game_communication_ids([game_id]))[game_id]
            if not self._is_game(comm_ids):
                raise InvalidParams()
            return comm_ids[0]

        return await self._psn_client.async_get_earned_trophies(
            await get_game_comm_id()
        )

    async def start_achievements_import(self, game_ids: List[TitleId]):
        if not self._http_client.is_authenticated:
            raise AuthenticationRequired
        await super().start_achievements_import(game_ids)

    async def import_games_achievements(self, game_ids: Iterable[TitleId]):
        try:
            games_cids = await self.get_game_communication_ids(game_ids)
            trophy_titles = await self._psn_client.get_trophy_titles()
        except ApplicationError as error:
            for title_id in game_ids:
                self.game_achievements_import_failure(title_id, error)
            return

        pending_cid_tids, pending_tid_cids, tid_trophies = self._process_trophies_cache(games_cids, trophy_titles)

        # process pending trophies
        requests = []
        for comm_id in pending_cid_tids.keys():
            timestamp = trophy_titles[comm_id]
            pending_tids = pending_cid_tids[comm_id]
            requests.append(self._import_trophies(comm_id, pending_tids, pending_tid_cids, tid_trophies, timestamp))

        await asyncio.gather(*requests)

        # log if some games has not been processed (it shouldn't happen)
        for tid in pending_tid_cids.keys():
            logging.error("Not fetched all trophies for game %s", tid)
            self.game_achievements_import_failure(tid, UnknownError())

    def _process_trophies_cache(
        self,
        games_cids: Dict[TitleId, Iterable[CommunicationId]],
        trophy_titles: TrophyTitles
    ) -> Tuple[_CID_TIDS_DICT, _TID_CIDS_DICT, _TID_TROPHIES_DICT]:
        pending_cid_tids: _CID_TIDS_DICT = defaultdict(set)
        pending_tid_cids: _TID_CIDS_DICT = defaultdict(set)
        tid_trophies: _TID_TROPHIES_DICT = {}

        for title_id, comm_ids in games_cids.items():
            if not self._is_game(comm_ids):
                self.game_achievements_import_failure(title_id, InvalidParams())
                continue

            game_trophies, pending_comm_ids = self._get_game_trophies_from_cache(comm_ids, trophy_titles)

            if pending_comm_ids:
                for comm_id in pending_comm_ids:
                    pending_cid_tids[comm_id].add(title_id)
                pending_tid_cids[title_id].update(pending_comm_ids)
                tid_trophies[title_id] = game_trophies
            else:
                # all trophies fetched from cache
                self.game_achievements_import_success(title_id, game_trophies)

        return pending_cid_tids, pending_tid_cids, tid_trophies

    def _get_game_trophies_from_cache(self, game_comm_ids, trophy_titles):
        """Process all communication ids for the game"""
        game_trophies: List[Achievement] = []
        pending_comm_ids: Set[CommunicationId] = set()
        for comm_id in set(game_comm_ids):
            last_update_time = trophy_titles.get(comm_id)
            if last_update_time is None:
                continue
            trophies = self._trophies_cache.get(comm_id, last_update_time)
            if trophies is None:
                pending_comm_ids.add(comm_id)
            else:
                game_trophies.extend(trophies)
        return game_trophies, pending_comm_ids

    async def _import_trophies(
        self,
        comm_id: CommunicationId,
        pending_tids: Set[TitleId],
        pending_tid_cids: _TID_CIDS_DICT,
        tid_trophies: _TID_TROPHIES_DICT,
        timestamp: UnixTimestamp
    ):
        def handle_error(error_):
            for tid_ in pending_tids:
                del pending_tid_cids[tid_]
                self.game_achievements_import_failure(tid_, error_)

        try:
            trophies: List[Achievement] = await self._psn_client.async_get_earned_trophies(comm_id)
            self._trophies_cache.update(comm_id, trophies, timestamp)
            while pending_tids:
                tid = pending_tids.pop()
                game_trophies = tid_trophies[tid]
                game_trophies.extend(trophies)
                pending_comm_ids = pending_tid_cids[tid]
                pending_comm_ids.remove(comm_id)
                if not pending_comm_ids:
                    # the game has already all comm ids processed
                    self.game_achievements_import_success(tid, game_trophies)
                    del pending_tid_cids[tid]
        except ApplicationError as error:
            handle_error(error)
        except Exception:
            logging.exception("Unhandled exception. Please report it to the plugin developers")
            handle_error(UnknownError())

    async def get_friends(self):
        return await self._psn_client.async_get_friends()

    def shutdown(self):
        asyncio.create_task(self._http_client.logout())


def main():
    create_and_run_plugin(PSNPlugin, sys.argv)


if __name__ == "__main__":
    main()
