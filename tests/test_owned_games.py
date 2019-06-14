import pytest
from galaxy.api.errors import AuthenticationRequired, UnknownBackendResponse
from http_client import paginate_url
from psn_client import DEFAULT_LIMIT, GAME_LIST_URL
from tests.async_mock import AsyncMock
from tests.test_data import COMMUNICATION_ID
from tests.test_data import GAMES, BACKEND_GAME_TITLES_WITHOUT_DLC


@pytest.mark.asyncio
async def test_not_authenticated(psn_plugin):
    with pytest.raises(AuthenticationRequired):
        await psn_plugin.get_owned_games()


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, games", [
    ({}, []),
    ({"titles": []}, []),
    (BACKEND_GAME_TITLES_WITHOUT_DLC, GAMES)
])
async def test_get_owned_games(
    http_get,
    authenticated_plugin,
    backend_response,
    games,
    mocker
):
    http_get.return_value = backend_response
    get_game_communication_id = mocker.patch(
        "plugin.PSNPlugin.get_game_communication_ids",
        new_callable=AsyncMock,
        return_value={game.game_id: COMMUNICATION_ID for game in GAMES}
    )

    assert games == await authenticated_plugin.get_owned_games()
    http_get.assert_called_once_with(
        paginate_url(GAME_LIST_URL.format(user_id="me"), DEFAULT_LIMIT))
    get_game_communication_id.assert_called_once_with([game.game_id for game in games])


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response", [
    {"titles": "bad_format"},
    {"titles": {"titleId": "CUSA07917_00"}},
    {"titles": {"name": "Tooth and Tail"}},
])
async def test_bad_format(
    http_get,
    authenticated_plugin,
    backend_response,
):
    http_get.return_value = backend_response
    with pytest.raises(UnknownBackendResponse):
        await authenticated_plugin.get_owned_games()

    http_get.assert_called_once_with(
        paginate_url(GAME_LIST_URL.format(user_id="me"), DEFAULT_LIMIT))
