import pytest
from galaxy.api.errors import UnknownBackendResponse
from galaxy.unittest.mock import async_return_value

from http_client import paginate_url
from psn_client import DEFAULT_LIMIT, GAME_LIST_URL
from tests.test_data import GAMES, BACKEND_GAME_TITLES, PARSED_GAME_TITLES


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, games", [
    pytest.param({"data": {"purchasedTitlesRetrieve": {"games": []}}}, [], id='no games'),
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
    http_get.assert_called_once_with(paginate_url(GAME_LIST_URL, DEFAULT_LIMIT))


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

    http_get.assert_called_once_with(paginate_url(GAME_LIST_URL, DEFAULT_LIMIT))
