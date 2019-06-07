import asyncio
import logging
import sys

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, NextStep, Achievement
from galaxy.api.consts import Platform
from galaxy.api.jsonrpc import InvalidParams
from galaxy.api.errors import ApplicationError, InvalidCredentials, UnknownError, AuthenticationRequired
from cache import Cache
from http_client import AuthenticatedHttpClient
from psn_client import (
    CommunicationId, TitleId,
    PSNClient, MAX_TITLE_IDS_PER_REQUEST, COMM_ID_NOT_AVAILABLE
)
from typing import Dict, List, Set, Iterable
from version import __version__

from http_client import OAUTH_LOGIN_URL, OAUTH_LOGIN_REDIRECT_URL

AUTH_PARAMS = {
    "window_title": "Login to My PlayStation\u2122",
    "window_width": 536,
    "window_height": 675,
    "start_uri": OAUTH_LOGIN_URL,
    "end_uri_regex": "^" + OAUTH_LOGIN_REDIRECT_URL + ".*"
}


class PSNPlugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.Psn, __version__, reader, writer, token)
        self._http_client = AuthenticatedHttpClient(self.lost_authentication)
        self._psn_client = PSNClient(self._http_client)
        self._comm_ids_cache: Dict[TitleId, CommunicationId] = {}
        self._trophies_cache = Cache()
        logging.getLogger("urllib3").setLevel(logging.FATAL)

    async def _do_auth(self, npsso):
        if not npsso:
            raise InvalidCredentials()

        try:
            await self._http_client.authenticate(npsso)
            user_id, user_name = await self._psn_client.async_get_own_user_info()
        except Exception:
            raise InvalidCredentials()

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
    def _is_game(comm_id: CommunicationId) -> bool:
        return comm_id != COMM_ID_NOT_AVAILABLE

    async def update_communication_id_cache(self, title_ids: List[TitleId]) -> Dict[TitleId, CommunicationId]:
        async def updater(title_id_slice: Iterable[TitleId]):
            delta.update(await self._psn_client.async_get_game_communication_id_map(title_id_slice))

        delta: Dict[TitleId, CommunicationId] = dict()
        await asyncio.gather(*[
            updater(title_ids[it:it + MAX_TITLE_IDS_PER_REQUEST])
            for it in range(0, len(title_ids), MAX_TITLE_IDS_PER_REQUEST)
        ])

        self._comm_ids_cache.update(delta)
        return delta

    async def get_game_communication_ids(self, title_ids: List[TitleId]) -> Dict[TitleId, CommunicationId]:
        result: Dict[TitleId, CommunicationId] = dict()
        misses: Set[TitleId] = set()
        for title_id in title_ids:
            comm_id: CommunicationId = self._comm_ids_cache.get(title_id)
            if comm_id:
                result[title_id] = comm_id
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
            comm_id: CommunicationId = (await self.get_game_communication_ids([game_id]))[game_id]
            if not self._is_game(comm_id):
                raise InvalidParams()

            return comm_id

        return await self._psn_client.async_get_earned_trophies(
            await get_game_comm_id()
        )

    async def start_achievements_import(self, game_ids: List[TitleId]):
        if not self._http_client.is_authenticated:
            raise AuthenticationRequired
        await super().start_achievements_import(game_ids)

    async def import_games_achievements(self, game_ids: Iterable[TitleId]):
        try:
            comm_ids = await self.get_game_communication_ids(game_ids)
            trophy_titles = await self._psn_client.get_trophy_titles()
        except ApplicationError as error:
            for game_id in game_ids:
                self.game_achievements_import_failure(game_id, error)

        # make a map
        trophy_titles = {trophy_title.communication_id: trophy_title for trophy_title in trophy_titles}
        requests = []
        for game_id, comm_id in comm_ids.items():
            if not self._is_game(comm_id):
                self.game_achievements_import_failure(game_id, InvalidParams())
                continue
            trophy_title = trophy_titles.get(comm_id)
            if trophy_title is None:
                self.game_achievements_import_success(game_id, [])
                continue
            trophies = self._trophies_cache.get(comm_id, trophy_title.last_update_time)
            if trophies is not None:
                self.game_achievements_import_success(game_id, trophies)
                continue
            requests.append(self._import_game_achievements(game_id, comm_id))
        await asyncio.gather(*requests)

    async def _import_game_achievements(self, title_id: TitleId, comm_id: CommunicationId):
        try:
            trophies: List[Achievement] = await self._psn_client.async_get_earned_trophies(comm_id)
            timestamp = max(trophy.unlock_time for trophy in trophies)
            self._trophies_cache.update(comm_id, trophies, timestamp)
            self.game_achievements_import_success(title_id, trophies)
        except ApplicationError as error:
            self.game_achievements_import_failure(title_id, error)
        except Exception:
            logging.exception("Unhandled exception. Please report it to the plugin developers")
            self.game_achievements_import_failure(title_id, UnknownError())

    async def get_friends(self):
        return await self._psn_client.async_get_friends()

    def shutdown(self):
        asyncio.create_task(self._http_client.logout())


def main():
    create_and_run_plugin(PSNPlugin, sys.argv)


if __name__ == "__main__":
    main()
