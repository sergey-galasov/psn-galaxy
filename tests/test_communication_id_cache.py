import pytest
import itertools
from galaxy.api.jsonrpc import InvalidParams
from plugin import COMM_ID_NOT_AVAILABLE
from psn_client import GAME_DETAILS_URL
from tests.async_mock import AsyncMock
from tests.test_data import GAMES, TITLE_TO_COMMUNICATION_ID, TITLES, UNLOCKED_ACHIEVEMENTS

GAME_ID = GAMES[0].game_id


@pytest.mark.asyncio
@pytest.fixture
async def mock_client_get_owned_games(mocker):
    mocked = mocker.patch(
        "plugin.PSNClient.async_get_owned_games",
        new_callable=AsyncMock,
        return_value=TITLES
    )
    yield mocked
    mocked.assert_called_once_with()


@pytest.mark.asyncio
@pytest.fixture
async def mock_get_game_communication_id_map(mocker):
    mocked = mocker.patch(
        "plugin.PSNClient.async_get_game_communication_id_map",
        new_callable=AsyncMock
    )
    yield mocked


@pytest.mark.asyncio
@pytest.fixture
def mock_client_get_earned_trophies(mocker):
    return mocker.patch(
        "plugin.PSNClient.async_get_earned_trophies",
        new_callable=AsyncMock,
    )


def comm_id_getter():
    for x in [
        dict(itertools.islice(TITLE_TO_COMMUNICATION_ID.items(), 5, 10)),
        dict(itertools.islice(TITLE_TO_COMMUNICATION_ID.items(), 0, 5)),
        dict(itertools.islice(TITLE_TO_COMMUNICATION_ID.items(), 10, 11)),
    ]:
        yield x


@pytest.mark.asyncio
async def test_empty_cache_on_games_retrieval(
    authenticated_plugin,
    mock_client_get_owned_games,
    mock_get_game_communication_id_map
):
    mock_get_game_communication_id_map.side_effect = comm_id_getter()

    assert {} == authenticated_plugin._comm_ids_cache
    assert GAMES == await authenticated_plugin.get_owned_games()
    assert TITLE_TO_COMMUNICATION_ID == authenticated_plugin._comm_ids_cache

    mock_calls_args = []
    for mock_call in mock_get_game_communication_id_map.call_args_list:
        args, kwargs = mock_call
        for a in args:
            mock_calls_args += a

    assert set(g.game_id for g in TITLES) == set(mock_calls_args)


@pytest.mark.asyncio
async def test_full_cache_on_games_retrieval(
    authenticated_plugin,
    mock_client_get_owned_games,
    mock_get_game_communication_id_map
):
    authenticated_plugin._comm_ids_cache = TITLE_TO_COMMUNICATION_ID.copy()
    assert GAMES == await authenticated_plugin.get_owned_games()
    assert TITLE_TO_COMMUNICATION_ID == authenticated_plugin._comm_ids_cache
    assert not mock_get_game_communication_id_map.called


@pytest.mark.asyncio
async def test_cache_miss_on_games_retrieval(
    authenticated_plugin,
    mock_client_get_owned_games,
    mock_get_game_communication_id_map
):
    border = int(len(TITLE_TO_COMMUNICATION_ID) / 2)
    authenticated_plugin._comm_ids_cache = dict(itertools.islice(TITLE_TO_COMMUNICATION_ID.items(), border))
    not_cached = dict(itertools.islice(TITLE_TO_COMMUNICATION_ID.items(), border, len(TITLE_TO_COMMUNICATION_ID)))

    mock_get_game_communication_id_map.return_value = {
        game_id: TITLE_TO_COMMUNICATION_ID[game_id] for game_id in not_cached
    }

    assert GAMES == await authenticated_plugin.get_owned_games()
    assert TITLE_TO_COMMUNICATION_ID == authenticated_plugin._comm_ids_cache

    mock_calls_args = []
    for mock_call in mock_get_game_communication_id_map.call_args_list:
        args, kwargs = mock_call
        for a in args:
            mock_calls_args += a

    assert set(not_cached) == set(mock_calls_args)


@pytest.mark.asyncio
async def test_cache_miss_on_dlc_achievements_retrieval(
    authenticated_plugin,
    mock_client_get_earned_trophies,
    mock_get_game_communication_id_map
):
    dlc_id = "some_dlc_id"
    mapping = {dlc_id: COMM_ID_NOT_AVAILABLE}
    mock_get_game_communication_id_map.return_value = mapping

    assert {} == authenticated_plugin._comm_ids_cache
    with pytest.raises(InvalidParams):
        await authenticated_plugin.get_unlocked_achievements(dlc_id)

    assert mapping == authenticated_plugin._comm_ids_cache

    assert not mock_client_get_earned_trophies.called
    mock_get_game_communication_id_map.assert_called_once_with([dlc_id])


@pytest.mark.asyncio
async def test_cache_miss_on_game_achievements_retrieval(
    authenticated_plugin,
    mock_client_get_earned_trophies,
    mock_get_game_communication_id_map
):
    comm_id = TITLE_TO_COMMUNICATION_ID[GAME_ID]
    mapping = {GAME_ID: comm_id}
    mock_get_game_communication_id_map.return_value = mapping
    mock_client_get_earned_trophies.return_value = UNLOCKED_ACHIEVEMENTS

    assert {} == authenticated_plugin._comm_ids_cache

    assert UNLOCKED_ACHIEVEMENTS == await authenticated_plugin.get_unlocked_achievements(GAME_ID)

    assert mapping == authenticated_plugin._comm_ids_cache

    mock_client_get_earned_trophies.assert_called_once_with(comm_id)
    mock_get_game_communication_id_map.assert_called_once_with([GAME_ID])


@pytest.mark.asyncio
async def test_cached_on_dlc_achievements_retrieval(
    authenticated_plugin,
    mock_client_get_earned_trophies,
    mock_get_game_communication_id_map
):
    dlc_id = "some_dlc_id"
    mapping = {dlc_id: COMM_ID_NOT_AVAILABLE}

    authenticated_plugin._comm_ids_cache = mapping
    with pytest.raises(InvalidParams):
        await authenticated_plugin.get_unlocked_achievements(dlc_id)

    assert mapping == authenticated_plugin._comm_ids_cache

    assert not mock_get_game_communication_id_map.called
    assert not mock_client_get_earned_trophies.called


@pytest.mark.asyncio
async def test_cached_on_game_achievements_retrieval(
    authenticated_plugin,
    mock_client_get_earned_trophies,
    mock_get_game_communication_id_map
):
    comm_id = TITLE_TO_COMMUNICATION_ID[GAME_ID]
    mapping = {GAME_ID: comm_id}

    mock_client_get_earned_trophies.return_value = UNLOCKED_ACHIEVEMENTS
    authenticated_plugin._comm_ids_cache = mapping.copy()

    assert UNLOCKED_ACHIEVEMENTS == await authenticated_plugin.get_unlocked_achievements(GAME_ID)

    assert not mock_get_game_communication_id_map.called
    assert mapping == authenticated_plugin._comm_ids_cache

    mock_client_get_earned_trophies.assert_called_once_with(comm_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, mapping", [
    ({}, {GAME_ID: COMM_ID_NOT_AVAILABLE}),
    ({"apps": []}, {GAME_ID: COMM_ID_NOT_AVAILABLE}),
    ({"apps": [{"npTitleId": GAME_ID}]}, {GAME_ID: COMM_ID_NOT_AVAILABLE}),
    ({"apps": [{"npTitleId": GAME_ID, "trophyTitles": []}]}, {GAME_ID: COMM_ID_NOT_AVAILABLE}),
    ({"apps": [{"npTitleId": GAME_ID, "trophyTitles": [{}]}]}, {GAME_ID: COMM_ID_NOT_AVAILABLE}),
    (
        {"apps": [{"npTitleId": GAME_ID, "trophyTitles": [{"npCommunicationId": COMM_ID_NOT_AVAILABLE}]}]},
        {GAME_ID: COMM_ID_NOT_AVAILABLE}
    ),
    (
        {"apps": [{"trophyTitles": [{"npCommunicationId": "NPWR12345_00"}]}]},
        {GAME_ID: COMM_ID_NOT_AVAILABLE}
    ),
    (
        {"apps": [{"npTitleId": None, "trophyTitles": [{"npCommunicationId": "NPWR23456_00"}]}]},
        {GAME_ID: COMM_ID_NOT_AVAILABLE}
    ),
    (
        {"apps": [{"npTitleId": GAME_ID, "trophyTitles": [{"npCommunicationId": "NPWR34567_00"}]}]},
        {GAME_ID: "NPWR34567_00"}
    ),
    (
        {"apps": [
            {"npTitleId": "CUSA07917_00", "trophyTitles": [{"npCommunicationId": "NPWR12784_00"}]},
            {"npTitleId": "CUSA07719_00", "trophyTitles": []},
            {"npTitleId": "CUSA02000_00", "trophyTitles": [{"npCommunicationId": "NPWR10584_00"}]}
        ]},
        {
            "CUSA07917_00": "NPWR12784_00",
            "CUSA07719_00": COMM_ID_NOT_AVAILABLE,
            "CUSA02000_00": "NPWR10584_00"
        }
    )
])
async def test_get_game_communication_id(
    http_get,
    authenticated_psn_client,
    backend_response,
    mapping
):
    http_get.return_value = backend_response
    assert mapping == await authenticated_psn_client.async_get_game_communication_id_map(mapping.keys())
    http_get.assert_called_once_with(GAME_DETAILS_URL.format(game_id_list=",".join(mapping.keys())))
