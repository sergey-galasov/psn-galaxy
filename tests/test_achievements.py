import asyncio
import pytest
from galaxy.api.errors import AuthenticationRequired, UnknownBackendResponse
from psn_client import EARNED_TROPHIES_PAGE
from tests.async_mock import AsyncMock
from unittest.mock import MagicMock
from tests.test_data import COMMUNICATION_ID, GAMES, TITLE_TO_COMMUNICATION_ID, UNLOCKED_ACHIEVEMENTS, CONTEXT, TROPHIES_CACHE, BACKEND_TROPHIES

GET_ALL_TROPHIES_URL = EARNED_TROPHIES_PAGE.format(communication_id=COMMUNICATION_ID, trophy_group_id="all")

GAME_ID = "CUSA07320_00"
GAME_IDS = [game.game_id for game in GAMES]

async def _wait_for_comm_ids_and_import_start():
    for i in range(7):
        await asyncio.sleep(0)

def _mock_get_game_communication_ids(mocker, mapping):
    return mocker.patch(
        "plugin.PSNPlugin.get_game_communication_ids",
        new_callable=AsyncMock,
        return_value=mapping
    )


@pytest.fixture
async def mock_get_game_communication_id(mocker):
    mocked = _mock_get_game_communication_ids(mocker, {GAME_ID: [COMMUNICATION_ID]})
    yield mocked
    mocked.assert_called_once_with([GAME_ID])


@pytest.fixture
async def mock_get_game_communication_ids(mocker):
    mocked = _mock_get_game_communication_ids(mocker, TITLE_TO_COMMUNICATION_ID)
    yield mocked


@pytest.fixture
def mock_async_get_game_communication_id_map(mocker):
    return mocker.patch("plugin.PSNClient.async_get_game_communication_id_map", new_callable=AsyncMock)

@pytest.fixture
def mock_async_get_earned_trophies(mocker):
    return mocker.patch("plugin.PSNClient.async_get_earned_trophies", new_callable=AsyncMock)

@pytest.fixture
def mock_get_trophy_titles(mocker):
    return mocker.patch("plugin.PSNClient.get_trophy_titles", new_callable=AsyncMock)

@pytest.fixture
def mock_import_achievements_success(mocker):
    return mocker.patch("plugin.PSNPlugin.game_achievements_import_success")


@pytest.fixture
def mock_import_achievements_failure(mocker):
    return mocker.patch("plugin.PSNPlugin.game_achievements_import_failure")


@pytest.mark.asyncio
async def test_not_authenticated(psn_plugin):
    with pytest.raises(AuthenticationRequired):
        await psn_plugin.prepare_achievements_context([GAME_ID])
        await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_get_unlocked_achievements(
    authenticated_plugin,
    mock_get_game_communication_ids,
):
    mock_get_game_communication_ids.return_value = TITLE_TO_COMMUNICATION_ID
    authenticated_plugin._trophies_cache = TROPHIES_CACHE
    assert UNLOCKED_ACHIEVEMENTS == await authenticated_plugin.get_unlocked_achievements(GAME_ID, CONTEXT)

@pytest.mark.asyncio
async def test_get_unlocked_achievements_trophies_cache_called(
    authenticated_plugin,
    mock_get_game_communication_ids
):
    mock_get_game_communication_ids.return_value = TITLE_TO_COMMUNICATION_ID
    authenticated_plugin._get_game_trophies_from_cache = MagicMock()

    await authenticated_plugin.get_unlocked_achievements(GAME_ID, CONTEXT)

    authenticated_plugin._get_game_trophies_from_cache.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, trophies", [
    ({}, []),
    ({"trophies": []}, []),
    ({"trophies": [{"trophyId": 42}]}, []),
    ({"trophies": [{"trophyId": 42, "fromUser": None}]}, []),
    ({"trophies": [{"trophyId": 42, "fromUser": {"onlineId": "user-id", "earned": False}}]}, []),
    ({"trophies": [{"trophyId": 42, "fromUser": {"onlineId": "user-id", "earned": False, "earnedDate": None}}]}, []),
    (BACKEND_TROPHIES, UNLOCKED_ACHIEVEMENTS)
])
async def test_async_get_earned_trophies(
    http_get,
    authenticated_psn_client,
    backend_response,
    trophies
):
    http_get.return_value = backend_response

    assert trophies == await authenticated_psn_client.async_get_earned_trophies(COMMUNICATION_ID)

    http_get.assert_called_once_with(GET_ALL_TROPHIES_URL)


@pytest.mark.asyncio
async def test_prepare_achievements_context_error(
    authenticated_plugin,
    mock_get_game_communication_ids,
    mock_async_get_earned_trophies
):
    mock_get_game_communication_ids.side_effect = UnknownBackendResponse()

    with pytest.raises(UnknownBackendResponse):
        await authenticated_plugin.prepare_achievements_context([GAME_ID])


@pytest.mark.asyncio
async def test_get_unlocked_achievements_no_context(
        authenticated_plugin,
        mock_get_game_communication_ids
):
    mock_get_game_communication_ids.return_value = TITLE_TO_COMMUNICATION_ID
    authenticated_plugin._trophies_cache = TROPHIES_CACHE
    assert [] == await authenticated_plugin.get_unlocked_achievements(GAME_ID, None)

@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response", [
    {"trophies": "bad_format"},
    {"trophies": {"bad": "format"}},
    {
        "trophies": [{
            "trophyName": "ach1",
            "fromUser": {"onlineId": "user-id", "earned": True, "earnedDate": "1987-02-07T10:14:42Z"}
        }]
    },
    {
        "trophies": [{
            "trophyId": 42, "trophyName": "ach2",
            "fromUser": {"onlineId": "user-id", "earned": True, "earnedDate": None}
        }]
    },
    {"trophies": [{"trophyId": 42, "trophyName": "ach2", "fromUser": {"onlineId": "user-id", "earned": True}}]},
])
async def test_async_get_earned_trophies_bad_format(
    authenticated_psn_client,
    http_get,
    backend_response,
):
    http_get.return_value = backend_response

    with pytest.raises(UnknownBackendResponse):
        await authenticated_psn_client.async_get_earned_trophies(COMMUNICATION_ID)

    http_get.assert_called_once_with(GET_ALL_TROPHIES_URL)


TROPHY_TITLES = {
    "NPWR12784_00": 1528464143,
    "NPWR11243_00": 1522265391,
    "NPWR07882_00": 1522236441,
    "NPWR07722_00": 1522220630,
    "NPWR10793_00": 1522203789,
    "NPWR10584_00": 1522162975,
    "NPWR07228_00": 1522151604,
    "NPWR11556_00": 1521718507
}

BACKEND_TROPHY_TITLES = {
    "totalResults": len(TROPHY_TITLES),
    "offset": 0,
    "limit": len(TROPHY_TITLES),
    "trophyTitles": [
        {
            "npCommunicationId": communication_id,
            "fromUser": {"lastUpdateDate": last_update_time}
        } for communication_id, last_update_time in (
            ("NPWR12784_00", "2018-06-08T13:22:23Z"),
            ("NPWR11243_00", "2018-03-28T19:29:51Z"),
            ("NPWR07882_00", "2018-03-28T11:27:21Z"),
            ("NPWR07722_00", "2018-03-28T07:03:50Z"),
            ("NPWR10793_00", "2018-03-28T02:23:09Z"),
            ("NPWR10584_00", "2018-03-27T15:02:55Z"),
            ("NPWR07228_00", "2018-03-27T11:53:24Z"),
            ("NPWR11556_00", "2018-03-22T11:35:07Z")
        )
    ]
}


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, trophy_titles", [
    ({}, {}),
    ({"trophyTitles": []}, {}),
    (BACKEND_TROPHY_TITLES, TROPHY_TITLES)
])
async def test_get_trophy_titles(
    http_get,
    authenticated_psn_client,
    backend_response,
    trophy_titles
):
    http_get.return_value = backend_response

    assert trophy_titles == await authenticated_psn_client.get_trophy_titles()

    http_get.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response", [
    {"trophyTitles": "bad_format"},
    {"trophyTitles": [{"no-npCommunicationId": None, "fromUser": {"lastUpdateDate": "2018-03-27T11:53:24Z"}}]},
    {"trophyTitles": [{"npCommunicationId": "NPWR12784_00", "fromUser": {"no-lastUpdateDate": None}}]}
])
async def test_get_trophy_titles_bad_format(
    http_get,
    authenticated_psn_client,
    backend_response
):
    http_get.return_value = backend_response

    with pytest.raises(UnknownBackendResponse):
        await authenticated_psn_client.get_trophy_titles()

    http_get.assert_called_once()
