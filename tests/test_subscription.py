import pytest
from galaxy.api.types import Subscription
from galaxy.api.errors import UnknownBackendResponse


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, status", [
    ({"profile": {"plus": 1}}, True),
    ({"profile": {"plus": 0}}, False),
])
async def test_get_psplus_status(
    http_get,
    authenticated_plugin,
    psplus_name,
    backend_response,
    status
):
    http_get.return_value = backend_response
    assert [Subscription(psplus_name, end_time=None, owned=status)] == \
        await authenticated_plugin.get_subscriptions()


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response", [
    {},
    {"profile": {}},
    {"profile": "bad_format"},
    {"profile": {"plus": "no"}},
    {"profile": {"plus": {}}},
])
async def test_bad_data(
    http_get,
    authenticated_plugin,
    backend_response
):
    http_get.return_value = backend_response
    with pytest.raises(UnknownBackendResponse):
        await authenticated_plugin.get_subscriptions()
