import asyncio
import pytest
from unittest.mock import Mock
from galaxy.api.errors import AuthenticationRequired
from http_client import AuthenticatedHttpClient
from tests.async_mock import AsyncMockDelayed, AsyncMock


@pytest.mark.asyncio
async def test_multiple_refreshing():
    EXPIRED_TOKEN = "old access token"
    REFRESHED_TOKEN = "refreshed access token"
    def raise_on_old_token(*args, **kwargs):
        if http_client._access_token == EXPIRED_TOKEN:
            raise AuthenticationRequired()
        return 'ok'
    http_client = AuthenticatedHttpClient(Mock, Mock)
    http_client._access_token = EXPIRED_TOKEN
    http_client.get_access_token = AsyncMockDelayed(return_value=REFRESHED_TOKEN)
    http_client._oauth_request = AsyncMock(side_effect=raise_on_old_token)
    responses = await asyncio.gather(
        http_client.request('url'),
        http_client.request('url'),
    )
    for i in responses:
        assert i == 'ok'


@pytest.mark.asyncio
async def test_logout_while_getting_access_token():
    http_client = AuthenticatedHttpClient(Mock, Mock)
    http_client.get_access_token = AsyncMock(return_value=Mock)
    def cancel_getting_access_token():
        http_client._getting_access_token.cancel()
    http_client._session.close = AsyncMock(side_effect=cancel_getting_access_token)

    await asyncio.gather(
        http_client._refresh_access_token(),
        http_client.logout()
    )
    assert http_client._getting_access_token.done() == True
    http_client.get_access_token.assert_called_once()

