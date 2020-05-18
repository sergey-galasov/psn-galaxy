import json
import pytest

from aioresponses import aioresponses
from galaxy.api.errors import AuthenticationRequired, InvalidCredentials, UnknownBackendResponse
from galaxy.api.types import Authentication, NextStep
from http import HTTPStatus
from plugin import AUTH_PARAMS
from psn_client import USER_INFO_URL
from tests.async_mock import AsyncMock

OWN_USER_INFO_URL = USER_INFO_URL.format(user_id="me")


@pytest.fixture
def backend_mock():
    with aioresponses() as response:
        yield response


@pytest.fixture()
def auth_info(account_id, online_id):
    return Authentication(account_id, online_id)


@pytest.fixture()
def get_access_token(mocker):
    return mocker.patch(
        "plugin.AuthenticatedHttpClient.get_access_token",
        new_callable=AsyncMock
    )


@pytest.mark.asyncio
async def test_no_stored_credentials(
    get_access_token,
    http_get,
    psn_plugin,
    access_token,
    stored_credentials,
    npsso,
    user_profile,
    auth_info,
    mocker
):
    assert NextStep("web_session", AUTH_PARAMS) == await psn_plugin.authenticate()

    get_access_token.return_value = access_token
    http_get.return_value = user_profile

    assert auth_info == await psn_plugin.pass_login_credentials(
        "whatever step",
        {},
        [{"name": "npsso", "value": npsso}]
    )

    get_access_token.assert_called_once_with(npsso)
    http_get.assert_called_once_with(OWN_USER_INFO_URL)


@pytest.mark.asyncio
async def test_stored_credentials(
    get_access_token,
    http_get,
    psn_plugin,
    access_token,
    stored_credentials,
    npsso,
    user_profile,
    auth_info
):
    get_access_token.return_value = access_token
    http_get.return_value = user_profile

    assert auth_info == await psn_plugin.authenticate(stored_credentials)

    get_access_token.assert_called_once_with(npsso)
    http_get.assert_called_once_with(OWN_USER_INFO_URL)


@pytest.mark.asyncio
async def test_failed_to_get_access_token_with_npsso(
    get_access_token,
    psn_plugin,
    stored_credentials,
    npsso
):
    get_access_token.side_effect = UnknownBackendResponse
    with pytest.raises(UnknownBackendResponse):
        assert await psn_plugin.authenticate(stored_credentials)
    get_access_token.assert_called_once_with(npsso)


@pytest.mark.asyncio
async def test_failed_to_get_user_info_during_auth(
    get_access_token,
    http_get,
    access_token,
    psn_plugin,
    stored_credentials,
    npsso
):
    get_access_token.return_value = access_token
    http_get.side_effect = UnknownBackendResponse
    with pytest.raises(UnknownBackendResponse):
        assert await psn_plugin.authenticate(stored_credentials)
    get_access_token.assert_called_once_with(npsso)


@pytest.mark.asyncio
async def test_invalid_authorization_response(
    get_access_token,
    psn_plugin,
    stored_credentials,
    npsso
):
    get_access_token.side_effect = InvalidCredentials
    with pytest.raises(InvalidCredentials):
        assert await psn_plugin.authenticate(stored_credentials)
    get_access_token.assert_called_once_with(npsso)


@pytest.mark.asyncio
async def test_invalid_access_token(
    get_access_token,
    psn_plugin,
    stored_credentials,
    npsso
):
    get_access_token.return_value = None
    with pytest.raises(UnknownBackendResponse):
        assert await psn_plugin.authenticate(stored_credentials)
    get_access_token.assert_called_once_with(npsso)


@pytest.mark.asyncio
async def test_refresh_access_token(
    backend_mock,
    authenticated_psn_client,
    user_profile,
    npsso,
    mocker
):
    backend_mock.get(OWN_USER_INFO_URL, status=HTTPStatus.UNAUTHORIZED)
    backend_mock.get(OWN_USER_INFO_URL, status=HTTPStatus.OK, body=json.dumps(user_profile))

    get_access_token = mocker.patch(
        "http_client.AuthenticatedHttpClient.get_access_token",
        new_callable=AsyncMock,
        return_value="new_access_token"
    )

    await authenticated_psn_client.async_get_own_user_info()

    get_access_token.assert_called_once_with(npsso)


@pytest.mark.asyncio
async def test_failed_to_refresh_access_token(
    backend_mock,
    authenticated_psn_client,
    npsso,
    mocker
):
    get_access_token = mocker.patch(
        "http_client.AuthenticatedHttpClient.get_access_token",
        new_callable=AsyncMock,
        side_effect=InvalidCredentials
    )
    backend_mock.get(OWN_USER_INFO_URL, status=HTTPStatus.UNAUTHORIZED)

    with pytest.raises(AuthenticationRequired):
        await authenticated_psn_client.async_get_own_user_info()

    get_access_token.assert_called_once_with(npsso)

