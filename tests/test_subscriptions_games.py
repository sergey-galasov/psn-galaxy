import pytest
from galaxy.api.errors import AuthenticationRequired

from tests.test_data import SUBSCRIPTION_GAMES, PSN_PLUS_MONTHLY_FREE_GAMES_HTML


@pytest.mark.asyncio
async def test_not_authenticated_subscriptions(psn_plugin):
    with pytest.raises(AuthenticationRequired):
        await psn_plugin.get_subscriptions()


@pytest.mark.asyncio
async def test_not_authenticated_subscription_games(psn_plugin, psplus_name):
    with pytest.raises(AuthenticationRequired):
        async for games in psn_plugin.get_subscription_games(psplus_name, None):
            pass


@pytest.mark.asyncio
async def test_get_subscription_games(
    http_get,
    authenticated_psn_client,
):
    http_get.return_value = PSN_PLUS_MONTHLY_FREE_GAMES_HTML
    assert SUBSCRIPTION_GAMES == await authenticated_psn_client.get_subscription_games()
    http_get.assert_called_once()
