from unittest.mock import Mock
from galaxy.api.errors import UnknownBackendResponse

import pytest
from galaxy.api.types import GameTime

from psn_client import parse_play_duration


@pytest.fixture()
def played_games_backend_response():
    return {"titles":
        [
            {
                "playDuration": "PT2H33M3S",
                "firstPlayedDateTime": "2021-02-27T13:17:31.460Z",
                "lastPlayedDateTime": "2021-03-06T16:29:22.490Z",
                "playCount": 5,
                "category": "unknown",
                "name": "Call of Duty®: Modern Warfare®",
                "titleId": "GAME_ID_1",
            },
            {
                "playDuration": "PT00H1M0S",
                "firstPlayedDateTime": "2021-02-27T13:17:31.460Z",
                "lastPlayedDateTime": "1970-01-01T00:00:01.000Z",
                "playCount": 5,
                "category": "unknown",
                "name": "Call of Duty®: Modern Warfare®",
                "titleId": "GAME_ID_2",
            },
        ]
    }


@pytest.mark.asyncio
async def test_prepare_game_times_context(
    http_get,
    authenticated_plugin,
    played_games_backend_response
):
    http_get.return_value = played_games_backend_response

    result = await authenticated_plugin.prepare_game_times_context(Mock(list))
    for title in played_games_backend_response['titles']:
        assert title in result.values()


@pytest.mark.asyncio
async def test_getting_game_time(
    http_get,
    authenticated_plugin,
    played_games_backend_response
):
    http_get.return_value = played_games_backend_response
    ctx = await authenticated_plugin.prepare_game_times_context(Mock(list))
    assert GameTime('GAME_ID_1', 154, 1615048162) == await authenticated_plugin.get_game_time('GAME_ID_1', ctx)
    assert GameTime('GAME_ID_2', 1, 1) == await authenticated_plugin.get_game_time('GAME_ID_2', ctx)


@pytest.mark.asyncio
@pytest.mark.parametrize("input_time, expected_result", [
        ("PT2H33M3S", 154),
        ("PT0H0M60S", 1),
        ("PT0H0M61S", 2),
        ("PT0H0M30S", 1),
        ("PT0H0M01S", 1),
        ("PT1H0M0S", 60),
        ("PT1H01M0S", 61),
        ("PT1H0M01S", 61),
        ("PT33H60M3S", 2041),
        ("PT1H4M", 64),
        ("PT1H1S", 61),
        ("PT30M0S", 30),
        ("PT0M1S", 1),
        ("PT1H", 60),
        ("PT1M", 1),
        ("PT1S", 1),
        ("1S", 1),
        ("PT0H0M0S", 0),
        ("PT", 0),
    ])
async def test_play_duration_parser(input_time, expected_result):
    minutes = parse_play_duration(input_time)
    assert minutes == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize("input_time", [
        None,
        "",
        "bad_value",
        "PTXH33M3S",
        "PT0HM3S",
        "PTHMS",
        "HMS",
    ])
async def test_unknown_foramat_of_play_duration_parser(input_time):
    with pytest.raises(UnknownBackendResponse):
        parse_play_duration(input_time)
