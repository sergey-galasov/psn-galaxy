from unittest.mock import Mock, patch
import json
import itertools

import pytest
from galaxy.api.jsonrpc import InvalidParams

from plugin import TROPHY_TITLE_INFO_CACHE_KEY, TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC, COMMUNICATION_IDS_CACHE_KEY
import serialization
from psn_client import GAME_DETAILS_URL, TrophyTitleInfo
from cache import Cache, CacheEntry
from tests.async_mock import AsyncMock
from tests.test_data import GAMES, TITLE_TO_TROPHY_TITLE, TITLES, UNLOCKED_ACHIEVEMENTS, CONTEXT, TROPHIES_CACHE, TITLE_TO_COMMUNICATION_ID

GAME_ID = GAMES[7].game_id


@pytest.fixture
def fixed_time():
    return 149037438


@pytest.fixture
def authenticated_plugin(mocker, authenticated_plugin, fixed_time):
    """authenticated_plugin with patched time.time"""
    mocker.patch('time.time', Mock(return_value=fixed_time))
    return authenticated_plugin


@pytest.fixture
def mock_client_get_owned_games(mocker):
    mocked = mocker.patch(
        "plugin.PSNClient.async_get_owned_games",
        new_callable=AsyncMock,
        return_value=TITLES
    )
    yield mocked


@pytest.fixture
def mock_get_game_trophy_title_info_map(mocker):
    mocked = mocker.patch(
        "plugin.PSNClient.async_get_game_trophy_title_info_map",
        new_callable=AsyncMock
    )
    yield mocked


@pytest.fixture
def mock_client_get_earned_trophies(mocker):
    return mocker.patch(
        "plugin.PSNClient.async_get_earned_trophies",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_persistent_cache(authenticated_plugin, mocker):
    return mocker.patch.object(type(authenticated_plugin), "persistent_cache", new_callable=mocker.PropertyMock)


def trophy_title_info_getter():
    for x in [
        dict(itertools.islice(TITLE_TO_TROPHY_TITLE.items(), 5, 10)),
        dict(itertools.islice(TITLE_TO_TROPHY_TITLE.items(), 0, 5)),
        dict(itertools.islice(TITLE_TO_TROPHY_TITLE.items(), 10, 12)),
    ]:
        yield x


@pytest.fixture
def mock_trophy_title_info_cache(fixed_time):
    cache = Cache()
    entires = {}
    invalidation_time = fixed_time + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC
    for k, v in TITLE_TO_TROPHY_TITLE.items():
        entires[k] = CacheEntry(value=v, timestamp=invalidation_time)
    cache._entries = entires
    return cache


@pytest.mark.asyncio
async def test_empty_cache_on_games_retrieval(
    authenticated_plugin,
    mock_client_get_owned_games,
    mock_get_game_trophy_title_info_map,
    mock_trophy_title_info_cache
):
    mock_get_game_trophy_title_info_map.side_effect = trophy_title_info_getter()

    assert TROPHY_TITLE_INFO_CACHE_KEY not in authenticated_plugin.persistent_cache
    assert GAMES == await authenticated_plugin.get_owned_games()
    assert mock_trophy_title_info_cache._entries == authenticated_plugin._trophy_title_info_cache._entries

    mock_calls_args = []
    for mock_call in mock_get_game_trophy_title_info_map.call_args_list:
        args, kwargs = mock_call
        for a in args:
            mock_calls_args += a

    assert set(g.game_id for g in TITLES) == set(mock_calls_args)


@pytest.mark.asyncio
async def test_full_cache_on_games_retrieval_cache_up_to_date(
    authenticated_plugin,
    mock_client_get_owned_games,
    mock_get_game_trophy_title_info_map,
    mock_trophy_title_info_cache,
):
    authenticated_plugin._trophy_title_info_cache = mock_trophy_title_info_cache
    assert GAMES == await authenticated_plugin.get_owned_games()
    assert not mock_get_game_trophy_title_info_map.called


@pytest.mark.asyncio
async def test_cache_miss_on_games_retrieval(
    authenticated_plugin,
    mock_client_get_owned_games,
    mock_get_game_trophy_title_info_map,
    mock_trophy_title_info_cache,
):
    border = int(len(TITLE_TO_TROPHY_TITLE) / 2)
    cached = dict(itertools.islice(mock_trophy_title_info_cache._entries.items(), 0, border))
    not_cached = dict(itertools.islice(TITLE_TO_TROPHY_TITLE.items(), border, len(TITLE_TO_TROPHY_TITLE)))

    authenticated_plugin._trophy_title_info_cache._entries = cached
    mock_get_game_trophy_title_info_map.return_value = {
        game_id: TITLE_TO_TROPHY_TITLE[game_id] for game_id in not_cached
    }

    assert GAMES == await authenticated_plugin.get_owned_games()
    assert mock_trophy_title_info_cache._entries == authenticated_plugin._trophy_title_info_cache._entries

    mock_calls_args = []
    for mock_call in mock_get_game_trophy_title_info_map.call_args_list:
        args, kwargs = mock_call
        for a in args:
            mock_calls_args += a

    assert set(not_cached) == set(mock_calls_args)


@pytest.mark.asyncio
async def test_cache_miss_on_dlc_achievements_retrieval(
    authenticated_plugin,
    mock_client_get_earned_trophies,
    mock_get_game_trophy_title_info_map
):
    dlc_id = "some_dlc_id"
    mapping = {dlc_id: []}
    mock_get_game_trophy_title_info_map.return_value = mapping

    assert TROPHY_TITLE_INFO_CACHE_KEY not in authenticated_plugin.persistent_cache
    with pytest.raises(InvalidParams):
        await authenticated_plugin.get_unlocked_achievements(dlc_id, CONTEXT)

    reloaded_cache = serialization.loads(authenticated_plugin.persistent_cache[TROPHY_TITLE_INFO_CACHE_KEY])
    assert reloaded_cache.get(dlc_id, 0) == mapping[dlc_id]

    assert not mock_client_get_earned_trophies.called
    mock_get_game_trophy_title_info_map.assert_called_once_with([dlc_id])


@pytest.mark.asyncio
async def test_cache_miss_on_game_achievements_retrieval(
    authenticated_plugin,
    mock_client_get_earned_trophies,
    mock_get_game_trophy_title_info_map
):
    comm_ids = TITLE_TO_TROPHY_TITLE[GAME_ID]
    mock_get_game_trophy_title_info_map.return_value = {GAME_ID: comm_ids}
    mock_client_get_earned_trophies.return_value = UNLOCKED_ACHIEVEMENTS
    authenticated_plugin._trophies_cache = TROPHIES_CACHE

    assert TROPHY_TITLE_INFO_CACHE_KEY not in authenticated_plugin.persistent_cache

    assert UNLOCKED_ACHIEVEMENTS == await authenticated_plugin.get_unlocked_achievements(GAME_ID, CONTEXT)

    reloaded_cache = serialization.loads(authenticated_plugin.persistent_cache[TROPHY_TITLE_INFO_CACHE_KEY])
    assert reloaded_cache.get(GAME_ID, 0) == comm_ids

    mock_get_game_trophy_title_info_map.assert_called_once_with([GAME_ID])


@pytest.mark.asyncio
async def test_cached_on_dlc_achievements_retrieval(
    authenticated_plugin,
    mock_client_get_earned_trophies,
    mock_get_game_trophy_title_info_map,
    fixed_time
):
    dlc_id = "some_dlc_id"
    mapping = {dlc_id: []}
    mock_get_game_trophy_title_info_map.return_value = mapping

    authenticated_plugin._trophy_title_info_cache.update(dlc_id, mapping[dlc_id], fixed_time)
    with pytest.raises(InvalidParams):
        await authenticated_plugin.get_unlocked_achievements(dlc_id, CONTEXT)

    assert not mock_get_game_trophy_title_info_map.called
    assert not mock_client_get_earned_trophies.called


@pytest.mark.asyncio
async def test_cached_on_game_achievements_retrieval(
    authenticated_plugin,
    mock_get_game_trophy_title_info_map,
    mock_trophy_title_info_cache
):
    comm_ids = TITLE_TO_TROPHY_TITLE[GAME_ID]
    mapping = {GAME_ID: comm_ids}
    mock_get_game_trophy_title_info_map.return_value = mapping

    authenticated_plugin._trophies_cache = TROPHIES_CACHE
    authenticated_plugin._trophy_title_info_cache = mock_trophy_title_info_cache

    assert UNLOCKED_ACHIEVEMENTS == await authenticated_plugin.get_unlocked_achievements(GAME_ID, CONTEXT)

    assert not mock_get_game_trophy_title_info_map.called


@pytest.mark.asyncio
async def test_cache_old_entry(
    authenticated_plugin,
    mock_client_get_owned_games,
    mock_get_game_trophy_title_info_map,
):
    async def get_owned_games_patched(now_time, games, title_ttis):
        def trophy_title_map_side_effect(titles):
            return {t: ttis for t, ttis in title_ttis.items() if t in titles}

        mock_client_get_owned_games.return_value = games
        mock_get_game_trophy_title_info_map.side_effect = trophy_title_map_side_effect
        with patch('time.time', Mock(return_value=now_time)):
            await authenticated_plugin.get_owned_games()

    def assert_trophy_title_info_cache(cache_entries):
        assert cache_entries == authenticated_plugin._trophy_title_info_cache._entries
    
    outdated_game, other_game = GAMES[0], GAMES[1]
    outdated_ttis, other_game_ttis = [], [TrophyTitleInfo("NPWR33322_00", Mock(str))]
    updated_ttis = [
        TrophyTitleInfo("NPWR11556_00", Mock(str)),
        TrophyTitleInfo("NPWR12507_00", Mock(str))
    ]

    # user has 1 game item that has no comm_id at all
    first_time = 140_000_000
    first_games = [outdated_game]
    first_title_cids = {outdated_game.game_id: outdated_ttis}
    await get_owned_games_patched(first_time, first_games, first_title_cids)
    assert_trophy_title_info_cache({
        outdated_game.game_id: CacheEntry(outdated_ttis, first_time + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC)
    })
    mock_get_game_trophy_title_info_map.assert_called_once_with([outdated_game.game_id])
    mock_get_game_trophy_title_info_map.reset_mock()

    # user buys other game; other_game title should be added to cache with second_time
    second_time = first_time + (TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC // 2)
    second_games = first_games + [other_game]
    second_title_cids = {**first_title_cids, other_game.game_id: other_game_ttis}
    await get_owned_games_patched(second_time, second_games, second_title_cids)
    assert_trophy_title_info_cache({
        outdated_game.game_id: CacheEntry(outdated_ttis, first_time + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC),
        other_game.game_id: CacheEntry(other_game_ttis, second_time + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC)
    })
    mock_get_game_trophy_title_info_map.assert_called_once_with([other_game.game_id])
    mock_get_game_trophy_title_info_map.reset_mock()
    
    # comm_ids cache for first title should be updated with third_time
    # other_game cache should not be updated as it is fresh enough
    third_time = first_time + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC + 5
    third_games = second_games
    third_title_cids = {**second_title_cids, GAMES[0].game_id: updated_ttis}
    await get_owned_games_patched(third_time, third_games, third_title_cids)
    assert_trophy_title_info_cache({
        outdated_game.game_id: CacheEntry(updated_ttis, third_time + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC),
        other_game.game_id: CacheEntry(other_game_ttis, second_time + TROPHY_TITLE_INFO_INVALIDATION_PERIOD_SEC)
    })
    mock_get_game_trophy_title_info_map.assert_called_once_with([outdated_game.game_id])


@pytest.mark.asyncio
async def test_cache_parsing(authenticated_plugin, mock_persistent_cache, mock_trophy_title_info_cache):
    mock_persistent_cache.return_value = {TROPHY_TITLE_INFO_CACHE_KEY: serialization.dumps(mock_trophy_title_info_cache)}
    authenticated_plugin.handshake_complete()
    assert authenticated_plugin._trophy_title_info_cache._entries == mock_trophy_title_info_cache._entries


@pytest.mark.asyncio
async def test_empty_cache_parsing(authenticated_plugin):
    authenticated_plugin.handshake_complete()
    assert authenticated_plugin.persistent_cache.get(TROPHY_TITLE_INFO_CACHE_KEY) == None
    assert authenticated_plugin._trophy_title_info_cache._entries == {}


@pytest.mark.asyncio
async def test_cache_parsing_migration(
    authenticated_plugin,
    mock_persistent_cache,
    mock_trophy_title_info_cache,
    mock_client_get_owned_games,
    mock_get_game_trophy_title_info_map,
):
    """
    Previous persistent_cache structure was a json string containing Dict[TitleId, List[CommunicationId]]
    A new persistent_cache structure is pickled Cache object with value of type Dict[TitleId, List[CommunicationId]]
    """
    mock_persistent_cache.return_value = {
        COMMUNICATION_IDS_CACHE_KEY: json.dumps(TITLE_TO_COMMUNICATION_ID)
    }
    authenticated_plugin.handshake_complete()
    assert COMMUNICATION_IDS_CACHE_KEY not in authenticated_plugin.persistent_cache

    # test new cache
    mock_get_game_trophy_title_info_map.side_effect = trophy_title_info_getter()
    assert GAMES == await authenticated_plugin.get_owned_games()
    assert mock_client_get_owned_games.called
    assert TROPHY_TITLE_INFO_CACHE_KEY in authenticated_plugin.persistent_cache
    assert authenticated_plugin._trophy_title_info_cache._entries == mock_trophy_title_info_cache._entries


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, mapping", [
    ({}, {GAME_ID: []}),
    ({"apps": []}, {GAME_ID: []}),
    ({"apps": [{"npTitleId": GAME_ID}]}, {GAME_ID: []}),
    ({"apps": [{"npTitleId": GAME_ID, "trophyTitles": []}]}, {GAME_ID: []}),
    ({"apps": [{"npTitleId": GAME_ID, "trophyTitles": [{}]}]}, {GAME_ID: []}),
    (
        {"apps": [{"trophyTitles": [{"npCommunicationId": "NPWR12345_00"}]}]},
        {GAME_ID: []}
    ),
    (
        {"apps": [{"npTitleId": None, "trophyTitles": [{"npCommunicationId": "NPWR23456_00"}]}]},
        {GAME_ID: []}
    ),
    (
        {"apps": [{"npTitleId": GAME_ID, "trophyTitles": [{"npCommunicationId": "NPWR34567_00"}]}]},
        {GAME_ID: [TrophyTitleInfo("NPWR34567_00", "")]}
    ),
    (
        {"apps": [{"npTitleId": GAME_ID, "trophyTitles": [{"npCommunicationId": "NPWR34567_00", "trophyTitleName": "Horizon Zero Down"}]}]},
        {GAME_ID: [TrophyTitleInfo("NPWR34567_00", "Horizon Zero Down")]}
    ),
    (
        {"apps": [
            {"npTitleId": "CUSA07917_00", "trophyTitles": [{"npCommunicationId": "NPWR12784_00"}]},
            {"npTitleId": "CUSA07719_00", "trophyTitles": []},
            {"npTitleId": "CUSA02000_00", "trophyTitles": [{"npCommunicationId": "NPWR10584_00", "trophyTitleName": "Horizon Zero Down"}]}
        ]},
        {
            "CUSA07917_00": [TrophyTitleInfo("NPWR12784_00", "")],
            "CUSA07719_00": [],
            "CUSA02000_00": [TrophyTitleInfo("NPWR10584_00", "Horizon Zero Down")]
        }
    ),
    (
            {"apps": [{"npTitleId": GAME_ID, "trophyTitles": [
                {"npCommunicationId": "NPWR34567_00", "trophyTitleName": "METAL GEAR SOLID V: THE PHANTOM PAIN"},
                {"npCommunicationId": "NPWR10584_00", "trophyTitleName": "METAL GEAR SOLID V: GROUND ZEROE"}
            ]}]},
            {GAME_ID: [
                TrophyTitleInfo("NPWR34567_00", "METAL GEAR SOLID V: THE PHANTOM PAIN"),
                TrophyTitleInfo("NPWR10584_00", "METAL GEAR SOLID V: GROUND ZEROE")
            ]}
    )
])
async def test_get_game_communication_id(
    http_get,
    authenticated_psn_client,
    backend_response,
    mapping
):
    http_get.return_value = backend_response
    assert mapping == await authenticated_psn_client.async_get_game_trophy_title_info_map(mapping.keys())
    http_get.assert_called_once_with(GAME_DETAILS_URL.format(game_id_list=",".join(mapping.keys())))
