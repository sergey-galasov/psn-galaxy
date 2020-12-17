import pytest
from galaxy.api.errors import AuthenticationRequired, UnknownBackendResponse
from galaxy.api.types import Game
from http_client import paginate_url
from psn_client import DEFAULT_LIMIT, GAME_LIST_URL, TrophyTitleInfo
from tests.async_mock import AsyncMock
from tests.test_data import GAMES, BACKEND_GAME_TITLES, TITLE_TO_TROPHY_TITLE, DEFAULT_LICENSE


@pytest.mark.asyncio
async def test_not_authenticated(psn_plugin):
    with pytest.raises(AuthenticationRequired):
        await psn_plugin.get_owned_games()


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, trophy_title_map, games", [
    pytest.param({"titles": []}, {}, [], id='no games'),
    pytest.param(
        {"titles": [
            {"titleId": "1", "name": None},  # no TrophyTitle
            {"titleId": "2", "name": None},  # multiple TrophyTitles
            {"titleId": "3", "name": None},  # single TrophyTitle
        ]},
        {
            "1": [],
            "2": [
                TrophyTitleInfo("a", "NARUTO: Ultimate Ninja STORM"),
                TrophyTitleInfo("b", "NARUTO SHIPPUDEN: Ultimate Ninja STORM 2"),
            ],
            "3": [
                TrophyTitleInfo("c", "Cyberpunk 2077")
            ]
        },
        [
            Game("3", "Cyberpunk 2077", [], DEFAULT_LICENSE)
        ],
        id="logic for lacking `name`"
    ),
    pytest.param(BACKEND_GAME_TITLES, TITLE_TO_TROPHY_TITLE, GAMES, id='multiple game: real case scenario'),
])
async def test_get_owned_games(
    http_get,
    authenticated_plugin,
    backend_response,
    games,
    trophy_title_map,
    mocker
):
    http_get.return_value = backend_response
    get_game_communication_id = mocker.patch(
        "plugin.PSNPlugin.get_game_trophies_map",
        new_callable=AsyncMock,
        return_value=trophy_title_map
    )

    assert games == await authenticated_plugin.get_owned_games()
    http_get.assert_called_once_with(
        paginate_url(GAME_LIST_URL.format(user_id="me"), DEFAULT_LIMIT))
    get_game_communication_id.assert_called_once_with([game['titleId'] for game in backend_response['titles']])


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
