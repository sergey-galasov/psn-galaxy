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
    http_client.can_refresh.set()
    http_client._access_token = EXPIRED_TOKEN
    http_client.get_access_token = AsyncMockDelayed(return_value=REFRESHED_TOKEN)
    http_client._oauth_request = AsyncMock(side_effect=raise_on_old_token)
    responses = await asyncio.gather(
        http_client.request('url'),
        http_client.request('url'),
    )
    for i in responses:
        assert i == 'ok'