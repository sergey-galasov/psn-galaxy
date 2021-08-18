from unittest.mock import MagicMock

import pytest
from galaxy.api.types import Authentication, NextStep
from galaxy.unittest.mock import async_return_value

from http_client import CookieJar
from plugin import AUTH_PARAMS
from psn_client import USER_INFO_URL


@pytest.fixture()
def auth_info(account_id, online_id):
    return Authentication(account_id, online_id)


@pytest.mark.asyncio
async def test_no_stored_credentials(
    http_get,
    psn_plugin,
    npsso,
    user_profile,
    auth_info,
):
    assert NextStep("web_session", AUTH_PARAMS) == await psn_plugin.authenticate()
    http_get.return_value = user_profile
    pass_login_credentials_result = await psn_plugin.pass_login_credentials(
        "whatever step",
        {},
        [{"name": "npsso", "value": npsso}]
    )

    assert pass_login_credentials_result == auth_info
    http_get.assert_called_with(USER_INFO_URL)


@pytest.mark.asyncio
async def test_with_stored_credentials(
    http_get,
    psn_plugin,
    stored_credentials,
    user_profile,
    auth_info,
):
    http_get.return_value = user_profile
    auth_result = await psn_plugin.authenticate(stored_credentials)

    assert auth_result == auth_info
    http_get.assert_called_with(USER_INFO_URL)


@pytest.mark.asyncio
async def test_credentials_to_store_after_refresh_cookies(
    user_profile,
    mocker,
    create_plugin
):
    new_credentials_to_store = {'cookies': {'npsso': 'new_npsso'}}
    cookie_jar = CookieJar()
    refresh_cookies = mocker.patch("http_client.HttpClient.refresh_cookies", return_value=async_return_value(None))
    mocker.patch("http_client.CookieJar", return_value=cookie_jar)
    plugin = await create_plugin()
    plugin.store_credentials = MagicMock()

    await plugin.authenticate({'cookies': {'npsso': 'old_npsso'}})
    # Because of mocked `refresh_cookies` method, this test has to manually trigger `update_cookies`.
    # In real code this method is triggered by `aiohttp.ClientSession._request` during preparing response.
    cookie_jar.update_cookies(new_credentials_to_store['cookies'])

    refresh_cookies.assert_called_once()
    plugin.store_credentials.assert_called_with(new_credentials_to_store)
