import pytest
from galaxy.api.errors import UnknownBackendResponse


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response", [
    {"data": {"oracleUserProfileRetrieve": {"isPsPlusMember": {}}}},
    {"data": {"oracleUserProfileRetrieve": {"isPsPlusMember": None}}},
    {"data": {"oracleUserProfileRetrieve": {"isPsPlusMember": "bad_format"}}},
])
async def test_psplus_bad_format(
    http_get,
    backend_response,
    authenticated_psn_client
):
    http_get.return_value = backend_response
    with pytest.raises(UnknownBackendResponse):
        await authenticated_psn_client.get_psplus_status()
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_get_psplus_status(
    http_get,
    authenticated_psn_client,
    user_profile
):
    http_get.return_value = user_profile
    assert True == await authenticated_psn_client.get_psplus_status()
    http_get.assert_called_once()
