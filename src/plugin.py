import asyncio
import time
import binascii
import logging
import pickle
import sys
from collections import defaultdict

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import Authentication, Game, NextStep, Achievement, UserPresence, PresenceState, SubscriptionGame, \
    Subscription, GameTime
from galaxy.api.consts import Platform
from galaxy.api.errors import ApplicationError, InvalidCredentials, UnknownError
from galaxy.api.jsonrpc import InvalidParams

import serialization
from cache import Cache
from http_client import AuthenticatedHttpClient
from psn_client import (
    CommunicationId, TitleId, TrophyTitles, UnixTimestamp, TrophyTitleInfo,
    PSNClient, MAX_TITLE_IDS_PER_REQUEST, parse_timestamp, parse_play_duration
)
from typing import Dict, List, Set, Iterable, Tuple, Optional, Any, AsyncGenerator
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

TROPHIES_CACHE_KEY = "trophies"
TROPHY_TITLE_INFO_CACHE_KEY = "trophy_title_info"
COMMUNICATION_IDS_CACHE_KEY = "communication_ids"  # deprecated
TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC = 3600 * 24 * 7


logger = logging.getLogger(__name__)


class PSNPlugin(Plugin):
    def __init__(self, reader, writer, token):
        super().__init__(Platform.Psn, __version__, reader, writer, token)
        self._http_client = AuthenticatedHttpClient(self.lost_authentication, self.store_credentials)
        self._psn_client = PSNClient(self._http_client)
        self._trophies_cache = Cache()
        self._trophy_title_info_cache = Cache()
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

        auth_info = await self._do_auth(stored_npsso)
        return auth_info

    async def pass_login_credentials(self, step, credentials, cookies):
        def get_npsso():
            for c in cookies:
                if c["name"] == "npsso" and c["value"]:
                    return c["value"]

        npsso = get_npsso()
        auth_info = await self._do_auth(npsso)
        return auth_info

    @staticmethod
    def _is_game(trophy_title_info: List[TrophyTitleInfo]) -> bool:
        """Assumption: all games has trophy info - otherwise it's DLC"""
        return trophy_title_info != []

    async def update_communication_id_cache(self, title_ids: List[TitleId]) \
            -> Dict[TitleId, List[TrophyTitleInfo]]:
        async def updater(title_id_slice: Iterable[TitleId]):
            delta.update(await self._psn_client.async_get_game_trophy_title_info_map(title_id_slice))

        delta: Dict[TitleId, List[TrophyTitleInfo]] = dict()
        await asyncio.gather(*[
            updater(title_ids[it:it + MAX_TITLE_IDS_PER_REQUEST])
            for it in range(0, len(title_ids), MAX_TITLE_IDS_PER_REQUEST)
        ])

        invalidate_time = UnixTimestamp(int(time.time()) + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC)
        for k, v in delta.items():
            self._trophy_title_info_cache.update(k, v, invalidate_time)
        try:
            self.persistent_cache[TROPHY_TITLE_INFO_CACHE_KEY] = serialization.dumps(self._trophy_title_info_cache)
            self.push_cache()
        except (pickle.PicklingError, binascii.Error):
            logging.error("Can not serialize communication ids cache")

        return delta

    async def get_game_trophies_map(self, title_ids: List[TitleId]) -> Dict[TitleId, List[TrophyTitleInfo]]:
        result: Dict[TitleId, List[TrophyTitleInfo]] = dict()
        need_update: Set[TitleId] = set()
        now = UnixTimestamp(int(time.time()))
        for title_id in title_ids:
            comm_ids: Optional[List[TrophyTitleInfo]] = self._trophy_title_info_cache.get(title_id, now)
            if comm_ids is not None:
                result[title_id] = comm_ids
            else:
                need_update.add(title_id)

        if need_update:
            result.update(await self.update_communication_id_cache(list(need_update)))

        return result

    async def get_subscriptions(self) -> List[Subscription]:
        is_plus_active = await self._psn_client.get_psplus_status()
        return [Subscription(subscription_name="PlayStation PLUS", end_time=None, owned=is_plus_active)]

    async def get_subscription_games(self, subscription_name: str, context: Any) -> AsyncGenerator[List[SubscriptionGame], None]:
        yield await self._psn_client.get_subscription_games()

    async def get_owned_games(self):
        async def filter_and_patch_games(titles: List[Game]) -> List[Game]:
            """Returns items with known title that are games (see `self._is_game`)
            In rare case where there is no `game_title`, borrow the name from TrophyTitle
            However ignores the item if it has multiple TrophyTitle's (comonly a bundle or other non-obvious case)
            """
            title_trophy_map = await self.get_game_trophies_map([t.game_id for t in titles])
            
            games = []
            for title in titles:
                ttis = title_trophy_map[title.game_id]
                if not self._is_game(ttis):
                    continue 
                if not title.game_title:
                    if len(ttis) == 1 and ttis[0].trophy_title_name:
                        title.game_title = ttis[0].trophy_title_name
                        logging.info("Patching title %s with its trophyTitleName %s", title, ttis[0].trophy_title_name)
                    else:
                        logging.warning("Ignoring title with unknown name %s having trophyTitles: %s", title, ttis)
                        continue
                games.append(title)
            return games

        return await filter_and_patch_games(
            await self._psn_client.async_get_owned_games()
        )

    async def get_unlocked_achievements(self, game_id: str, context: Any) -> List[Achievement]:
        if not context:
            return []
        trophy_title_infos: List[TrophyTitleInfo] = (await self.get_game_trophies_map([game_id]))[game_id]
        if not self._is_game(trophy_title_infos):
            raise InvalidParams()
        return self._get_game_trophies_from_cache([tti.communication_id for tti in trophy_title_infos], context)[0]

    async def prepare_achievements_context(self, game_ids: List[str]) -> Any:
        games_cids = {
            title_id: [tti.communication_id for tti in ttis]
            for title_id, ttis in (await self.get_game_trophies_map(game_ids)).items()
        }
        trophy_titles = await self._psn_client.get_trophy_titles()

        pending_cid_tids, pending_tid_cids, tid_trophies = self._process_trophies_cache(games_cids, trophy_titles)

        # process pending trophies
        requests = []
        for comm_id in pending_cid_tids.keys():
            timestamp = trophy_titles[comm_id]
            pending_tids = pending_cid_tids[comm_id]
            requests.append(self._import_trophies(comm_id, pending_tids, pending_tid_cids, tid_trophies, timestamp))

        await asyncio.gather(*requests)

        # update cache
        if requests:
            try:
                self.persistent_cache[TROPHIES_CACHE_KEY] = serialization.dumps(self._trophies_cache)
                self.push_cache()
            except (pickle.PicklingError, binascii.Error):
                logging.error("Can not serialize trophies cache")

        return trophy_titles

    def _process_trophies_cache(
        self,
        games_cids: Dict[TitleId, Iterable[CommunicationId]],
        trophy_titles: TrophyTitles
    ) -> Tuple[_CID_TIDS_DICT, _TID_CIDS_DICT, _TID_TROPHIES_DICT]:
        pending_cid_tids: _CID_TIDS_DICT = defaultdict(set)
        pending_tid_cids: _TID_CIDS_DICT = defaultdict(set)
        tid_trophies: _TID_TROPHIES_DICT = {}

        for title_id, comm_ids in games_cids.items():

            game_trophies, pending_comm_ids = self._get_game_trophies_from_cache(comm_ids, trophy_titles)

            if pending_comm_ids:
                for comm_id in pending_comm_ids:
                    pending_cid_tids[comm_id].add(title_id)
                pending_tid_cids[title_id].update(pending_comm_ids)
                tid_trophies[title_id] = game_trophies

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
                    del pending_tid_cids[tid]
        except ApplicationError as error:
            handle_error(error)
        except Exception:
            logging.exception("Unhandled exception. Please report it to the plugin developers")
            handle_error(UnknownError())

    async def prepare_game_times_context(self, game_ids: List[str]) -> Any:
        return {game['titleId']: game for game in await self._psn_client.async_get_played_games()}

    async def get_game_time(self, game_id: str, context: Any) -> GameTime:
        time_played, last_played_game = None, None
        try:
            game = context[game_id]
            last_played_game = parse_timestamp(game['lastPlayedDateTime'])
            time_played = parse_play_duration(game['playDuration'])
        except KeyError as e:
            logger.debug(e)
        return GameTime(game_id, time_played, last_played_game)

    async def prepare_user_presence_context(self, user_ids: List[str]) -> Any:
        return await self._psn_client.async_get_friends_presences()

    async def get_user_presence(self, user_id: str, context: Any) -> UserPresence:
        for user in context:
            if user_id in user:
                return user[user_id]
        return UserPresence(PresenceState.Unknown)

    async def get_friends(self):
        return await self._psn_client.async_get_friends()

    async def shutdown(self):
        await self._http_client.logout()

    def handshake_complete(self):
        trophies_cache = self.persistent_cache.get(TROPHIES_CACHE_KEY)
        if trophies_cache is not None:
            try:
                self._trophies_cache = serialization.loads(trophies_cache)
            except (pickle.UnpicklingError, binascii.Error):
                logging.exception("Can not deserialize trophies cache")

        tti_cache = self.persistent_cache.get(TROPHY_TITLE_INFO_CACHE_KEY)
        if tti_cache is not None:
            try:
                self._trophy_title_info_cache = serialization.loads(tti_cache)
            except (pickle.UnpicklingError, binascii.Error):
                logging.exception("Can not deserialize communication ids cache")

        comm_ids_cache = self.persistent_cache.get(COMMUNICATION_IDS_CACHE_KEY)
        if comm_ids_cache:
            logging.info("Removing communication_ids cache in favor of new trophy_title_info cache")
            del self.persistent_cache[COMMUNICATION_IDS_CACHE_KEY]


def main():
    create_and_run_plugin(PSNPlugin, sys.argv)


if __name__ == "__main__":
    main()
