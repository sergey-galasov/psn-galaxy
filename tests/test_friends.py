import pytest
from galaxy.api.errors import AuthenticationRequired, UnknownBackendResponse
from psn_client import DEFAULT_LIMIT, FRIENDS_URL
from http_client import paginate_url
from tests.test_data import BACKEND_USER_PROFILES, FRIEND_INFO_LIST

GET_ALL_FRIENDS_URL = paginate_url(FRIENDS_URL.format(user_id="me"), limit=DEFAULT_LIMIT)


def test_not_authenticated(psn_plugin, event_loop):
    with pytest.raises(AuthenticationRequired):
        event_loop.run_until_complete(psn_plugin.get_friends())


@pytest.mark.asyncio
async def test_empty_response(
    http_get,
    authenticated_plugin
):
    http_get.return_value = {}

    assert [] == await authenticated_plugin.get_friends()
    http_get.assert_called_once_with(GET_ALL_FRIENDS_URL)


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response", [
    {"profiles": "bad_format"},
    {"profiles": ["bad_format"]},
    {"profiles": [{
        "accountId": "user-id",
        "no-onlineId": "username"
    }]},
    {"profiles": [{
        "no-accountId": "user-id",
        "onlineId": "username"
    }]}
])
async def test_bad_format(
    http_get,
    authenticated_plugin,
    backend_response
):
    http_get.return_value = backend_response
    with pytest.raises(UnknownBackendResponse):
        await authenticated_plugin.get_friends()

    http_get.assert_called_once_with(GET_ALL_FRIENDS_URL)


@pytest.mark.asyncio
@pytest.mark.parametrize("backend_response, friend_list", [
    ({}, []),
    ({"profiles": []}, []),
    (BACKEND_USER_PROFILES, FRIEND_INFO_LIST)
])
async def test_get_friends(
    http_get,
    authenticated_plugin,
    backend_response,
    friend_list
):
    http_get.return_value = backend_response
    assert friend_list == await authenticated_plugin.get_friends()
    http_get.assert_called_once_with(GET_ALL_FRIENDS_URL)
