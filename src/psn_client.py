import asyncio
import logging
import math
import re
from datetime import datetime, timezone, timedelta
from functools import partial
from typing import List, NewType, Optional

from galaxy.api.errors import UnknownBackendResponse
from galaxy.api.types import SubscriptionGame

from http_client import paginate_url
from parsers import PSNGamesParser

GAME_LIST_URL = "https://web.np.playstation.com/api/graphql/v1/op" \
                "?operationName=getPurchasedGameList" \
                '&variables={"isActive":true,"platform":["ps3","ps4","ps5"],"subscriptionService":"NONE"}' \
                '&extensions={"persistedQuery":{"version":1,"sha256Hash":"2c045408b0a4d0264bb5a3edfed4efd49fb4749cf8d216be9043768adff905e2"}}'

PLAYED_GAME_LIST_URL = "https://web.np.playstation.com/api/graphql/v1/op" \
                       "?operationName=getUserGameList" \
                       '&variables={"limit":50,"categories":"ps3_game,ps4_game,ps5_native_game"}' \
                       '&extensions={"persistedQuery":{"version":1,"sha256Hash":"e780a6d8b921ef0c59ec01ea5c5255671272ca0d819edb61320914cf7a78b3ae"}}'

USER_INFO_URL = "https://web.np.playstation.com/api/graphql/v1/op" \
                "?operationName=getProfileOracle" \
                "&variables={}" \
                '&extensions={"persistedQuery":{"version":1,"sha256Hash":"c17b8b45ac988fec34e6a833f7a788edf7857c900fc3dc116585ced48577fb05"}}'

PSN_PLUS_SUBSCRIPTIONS_URL = 'https://store.playstation.com/subscriptions'

DEFAULT_LIMIT = 100

TitleId = NewType("TitleId", str)
UnixTimestamp = NewType("UnixTimestamp", int)


def parse_timestamp(earned_date) -> UnixTimestamp:
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ" if '.' in earned_date else "%Y-%m-%dT%H:%M:%SZ"
    dt = datetime.strptime(earned_date, date_format)
    dt = datetime.combine(dt.date(), dt.time(), timezone.utc)
    return UnixTimestamp(int(dt.timestamp()))


def parse_play_duration(duration: Optional[str]) -> int:
    """Returns time of played game in minutes from PSN API format `PT{HOURS}H{MINUTES}M{SECONDS}S`. Example: `PT2H33M3S`"""
    if not duration:
        raise UnknownBackendResponse(f'nullable playtime duration: {type(duration)}')
    try:
        result = re.match(
            r'(?:PT)?'
            r'(?:(?P<hours>\d*)H)?'
            r'(?:(?P<minutes>\d*)M)?'
            r'(?:(?P<seconds>\d*)S)?$',
            duration
        )
        mapped_result = {k: float(v) for k, v in result.groupdict(0).items()}
        time = timedelta(**mapped_result)
    except (ValueError, AttributeError, TypeError):
        raise UnknownBackendResponse(f'Unmatchable gametime: {duration}')
        
    total_minutes = math.ceil(time.seconds / 60 + time.days * 24 * 60)
    return total_minutes


def date_today():
    return datetime.today()


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
            logging.debug(f'user profile data: {response}')
            try:
                return response["data"]["oracleUserProfileRetrieve"]["accountId"], \
                       response["data"]["oracleUserProfileRetrieve"]["onlineId"]
            except (KeyError, TypeError) as e:
                raise UnknownBackendResponse(e)
        return await self.fetch_data(
            user_info_parser,
            USER_INFO_URL,
        )

    async def get_psplus_status(self) -> bool:

        def user_subscription_parser(response):
            try:
                status = response["data"]["oracleUserProfileRetrieve"]['isPsPlusMember']
                if status in [0, 1, True, False]:
                    return bool(status)
                raise TypeError
            except (KeyError, TypeError) as e:
                raise UnknownBackendResponse(e)

        return await self.fetch_data(
            user_subscription_parser,
            USER_INFO_URL,
        )

    async def async_get_purchased_games(self):
        def games_parser(response):
            try:
                games = response['data']['purchasedTitlesRetrieve']['games']
                return [
                    {"titleId": title["titleId"], "name": title["name"]} for title in games
                ] if games else []
            except (KeyError, TypeError) as e:
                raise UnknownBackendResponse(e)

        return await self.fetch_paginated_data(games_parser, GAME_LIST_URL, "totalCount")

    async def get_subscription_games(self) -> List[SubscriptionGame]:
        return await self.fetch_data(PSNGamesParser().parse, PSN_PLUS_SUBSCRIPTIONS_URL, get_json=False, silent=True)

    async def async_get_played_games(self):
        def games_parser(response):
            try:
                games = response['data']['gameLibraryTitlesRetrieve']['games']
                return [
                    {"titleId": title["titleId"], "name": title["name"]} for title in games
                ] if games else []
            except (KeyError, TypeError) as e:
                raise UnknownBackendResponse(e)

        return await self.fetch_paginated_data(games_parser, PLAYED_GAME_LIST_URL, 'totalItemCount')
