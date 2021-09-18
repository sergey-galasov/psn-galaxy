import copy

import pytest
from galaxy.api.consts import LicenseType
from galaxy.api.errors import UnknownBackendResponse
from galaxy.api.types import Game, LicenseInfo
from galaxy.unittest.mock import async_return_value

from tests.test_data import GAMES, BACKEND_GAME_TITLES, PARSED_GAME_TITLES


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, games", [
    pytest.param({"data": {"purchasedTitlesRetrieve": {"games": [], "pageInfo":{"totalResults": 0}}}}, [], id='no games'),
    pytest.param(BACKEND_GAME_TITLES, GAMES, id='multiple game: real case scenario'),
])
async def test_get_owned_games__only_purchased_games(
    authenticated_plugin,
    http_get,
    backend_response,
    games,
    mocker
):
    http_get.return_value = backend_response
    mocker.patch(
        "psn_client.PSNClient.async_get_played_games",
        return_value=async_return_value([])
    )

    assert games == await authenticated_plugin.get_owned_games()


@pytest.mark.asyncio
@pytest.mark.parametrize("parsed_purchased_games_titles,parsed_played_games_titles,games", [
    pytest.param(PARSED_GAME_TITLES, [], GAMES, id='only purchased games'),
    pytest.param([], PARSED_GAME_TITLES, GAMES, id='only played games'),
    pytest.param(PARSED_GAME_TITLES, PARSED_GAME_TITLES, GAMES, id='played and purchased games'),
    pytest.param([], [], [], id='no games'),
])
async def test_get_purchased_and_played_games(
    authenticated_plugin,
    games,
    mocker,
    parsed_purchased_games_titles,
    parsed_played_games_titles,
):
    mocker.patch(
        "psn_client.PSNClient.async_get_purchased_games",
        return_value=async_return_value(parsed_purchased_games_titles)
    )
    mocker.patch(
        "psn_client.PSNClient.async_get_played_games",
        return_value=async_return_value(parsed_played_games_titles)
    )
    assert await authenticated_plugin.get_owned_games() == games


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response", [
    {"data": "bad_format"},
    {"data": {"purchasedTitlesRetrieve": "CUSA07917_00"}},
    {"data": {"purchasedTitlesRetrieve": {"games": "CUSA07917_00"}}},
    {"data": {"name": "Tooth and Tail"}},
])
async def test_bad_format(
    authenticated_plugin,
    http_get,
    backend_response,
):
    http_get.return_value = backend_response
    with pytest.raises(UnknownBackendResponse):
        await authenticated_plugin.get_owned_games()


async def test_fetch_200_purchased_games(
    authenticated_plugin,
    mocker,
    http_get
):
    mocker.patch(
        "psn_client.PSNClient.async_get_played_games",
        return_value=async_return_value([])
    )
    response_size = 100
    purchased_games = [{"titleId": f"GAME_ID_{i}", "name": f"GAME_NAME_{i}"} for i in range(200)]
    response = {
        "data": {
            "purchasedTitlesRetrieve": {
                "games": [],
                "pageInfo":  {
                    "totalCount": len(purchased_games),
                    "size": response_size,
                }
            }
        }
    }
    r1, r2 = copy.deepcopy(response), copy.deepcopy(response)
    r1["data"]["purchasedTitlesRetrieve"]["games"] = purchased_games[:response_size]
    r2["data"]["purchasedTitlesRetrieve"]["games"] = purchased_games[response_size:]
    http_get.side_effect = [r1, r2]
    expected_games = [
        Game(game["titleId"], game["name"], [], LicenseInfo(LicenseType.SinglePurchase, None)) for game in purchased_games
    ]

    assert await authenticated_plugin.get_owned_games() == expected_games
