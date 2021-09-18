import pytest

from tests.test_data import SUBSCRIPTION_GAMES, PSN_PLUS_MONTHLY_FREE_GAMES_HTML


@pytest.mark.asyncio
async def test_get_subscription_games(
    http_get,
    authenticated_psn_client,
):
    http_get.return_value = PSN_PLUS_MONTHLY_FREE_GAMES_HTML
    assert SUBSCRIPTION_GAMES == await authenticated_psn_client.get_subscription_games()
    http_get.assert_called_once()
