import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from typing import Dict, List, NewType

from galaxy.api.errors import UnknownBackendResponse
from galaxy.api.types import Achievement, Game, LicenseInfo, FriendInfo
from galaxy.api.consts import LicenseType
from http_client import paginate_url

# game_id_list is limited to 5 IDs per request
GAME_DETAILS_URL = "https://pl-tpy.np.community.playstation.net/trophy/v1/apps/trophyTitles" \
    "?npTitleIds={game_id_list}" \
    "&fields=@default" \
    "&npLanguage=en"

GAME_LIST_URL = "https://gamelist.api.playstation.com/v1/users/{user_id}/titles" \
    "?type=owned,played" \
    "&app=richProfile" \
    "&sort=-lastPlayedDate" \
    "&iw=240"\
    "&ih=240"\
    "&fields=@default"

TROPHY_TITLES_URL = "https://pl-tpy.np.community.playstation.net/trophy/v1/trophyTitles"

EARNED_TROPHIES_PAGE = "https://pl-tpy.np.community.playstation.net/trophy/v1/" \
    "trophyTitles/{communication_id}/trophyGroups/{trophy_group_id}/trophies?" \
    "fields=@default,trophyRare,trophyEarnedRate,trophySmallIconUrl,groupId" \
    "&visibleType=1" \
    "&npLanguage=en"

USER_INFO_URL = "https://pl-prof.np.community.playstation.net/userProfile/v1/users/{user_id}/profile2" \
    "?fields=accountId,onlineId"

FRIENDS_URL = "https://us-prof.np.community.playstation.net/userProfile/v1/users/{user_id}/friends/profiles2" \
    "?fields=accountId,onlineId"

DEFAULT_LIMIT = 100
MAX_TITLE_IDS_PER_REQUEST = 5
COMM_ID_NOT_AVAILABLE = "-N/A-"

CommunicationId = NewType("CommunicationId", str)
TitleId = NewType("TitleId", str)
UnixTimestamp = NewType("UnixTimestamp", int)


def parse_timestamp(earned_date) -> UnixTimestamp:
    dt = datetime.strptime(earned_date, "%Y-%m-%dT%H:%M:%SZ")
    dt = datetime.combine(dt.date(), dt.time(), timezone.utc)
    return UnixTimestamp(dt.timestamp())


@dataclass
class TrophyTitle:
    communication_id: CommunicationId
    last_update_time: UnixTimestamp


class PSNClient:
    def __init__(self, http_client):
        self._http_client = http_client

    @staticmethod
    async def _async(method, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(method, *args, **kwargs))

    async def fetch_paginated_data(
        self,
        parser,
        url,
        counter_name,
        limit=DEFAULT_LIMIT,
        *args,
        **kwargs
    ):
        response = await self._http_client.get(paginate_url(url=url, limit=limit), *args, **kwargs)
        if not response:
            return []

        try:
            total = int(response.get(counter_name, 0))
        except ValueError:
            raise UnknownBackendResponse()

        responses = [response] + await asyncio.gather(*[
            self._http_client.get(paginate_url(url=url, limit=limit, offset=offset), *args, **kwargs)
            for offset in range(limit, total, limit)
        ])

        try:
            return [rec for res in responses for rec in parser(res)]
        except Exception:
            logging.exception("Cannot parse data")
            raise UnknownBackendResponse()

    async def fetch_data(self, parser, *args, **kwargs):
        response = await self._http_client.get(*args, **kwargs)

        try:
            return parser(response)
        except Exception:
            logging.exception("Cannot parse data")
            raise UnknownBackendResponse()

    async def async_get_own_user_info(self):
        def user_info_parser(response):
            return response["profile"]["accountId"], response["profile"]["onlineId"]

        return await self.fetch_data(
            user_info_parser,
            USER_INFO_URL.format(user_id="me")
        )

    async def async_get_owned_games(self):
        def game_parser(title):
            return Game(
                game_id=title["titleId"],
                game_title=title["name"],
                dlcs=[],
                license_info=LicenseInfo(LicenseType.SinglePurchase, None)
            )

        def games_parser(response):
            return [
                game_parser(title) for title in response["titles"]
            ] if response else []

        return await self.fetch_paginated_data(
            games_parser,
            GAME_LIST_URL.format(user_id="me"),
            "totalResults"
        )

    async def async_get_game_communication_id_map(self, game_ids: List[TitleId]) -> Dict[TitleId, CommunicationId]:
        def communication_ids_parser(response):
            def get_comm_id(trophy_titles):
                if not trophy_titles:
                    return COMM_ID_NOT_AVAILABLE
                return trophy_titles[0].get("npCommunicationId", COMM_ID_NOT_AVAILABLE)

            try:
                return {
                    app["npTitleId"]: get_comm_id(app["trophyTitles"])
                    for app in response["apps"]
                } if response else {}
            except (KeyError, IndexError):
                return {}

        mapping = await self.fetch_data(
            communication_ids_parser,
            GAME_DETAILS_URL.format(game_id_list=",".join(game_ids))
        )

        return {
            game_id: mapping.get(game_id, COMM_ID_NOT_AVAILABLE)
            for game_id in game_ids
        }

    async def get_trophy_titles(self) -> List[TrophyTitle]:
        def title_parser(title) -> TrophyTitle:
            return TrophyTitle(
                communication_id=title["npCommunicationId"],
                last_update_time=parse_timestamp((title.get("fromUser") or {})["lastUpdateDate"])
            )

        def titles_parser(response) -> List[TrophyTitle]:
            return [
                title_parser(title) for title in response.get("trophyTitles", [])
            ] if response else []

        return await self.fetch_paginated_data(
            parser=titles_parser,
            url=TROPHY_TITLES_URL,
            counter_name="totalResults",
            params={
                "fields": "@default",
                "platform": "PS4",
                "npLanguage": "en"
            }
        )

    async def async_get_earned_trophies(self, communication_id) -> List[Achievement]:
        def trophy_parser(trophy) -> Achievement:
            return Achievement(
                achievement_id=str(trophy["trophyId"]),
                achievement_name=str(trophy["trophyName"]),
                unlock_time=parse_timestamp(trophy["fromUser"]["earnedDate"])
            )

        def trophies_parser(response) -> List[Achievement]:
            return [
                trophy_parser(trophy) for trophy in response.get("trophies", [])
                if trophy.get("fromUser") and trophy["fromUser"].get("earned")
            ] if response else []

        return await self.fetch_data(trophies_parser, EARNED_TROPHIES_PAGE.format(
            communication_id=communication_id,
            trophy_group_id="all"))

    async def async_get_friends(self):
        def friend_info_parser(profile):
            return FriendInfo(
                user_id=str(profile["accountId"]),
                user_name=str(profile["onlineId"])
            )

        def friend_list_parser(response):
            return [
                friend_info_parser(profile) for profile in response.get("profiles", [])
            ] if response else []

        return await self.fetch_paginated_data(
            friend_list_parser,
            FRIENDS_URL.format(user_id="me"),
            "totalResults"
        )
