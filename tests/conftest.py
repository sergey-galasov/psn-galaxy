import pytest
from galaxy.unittest.mock import async_return_value

from plugin import PSNClient, PSNPlugin
from unittest.mock import MagicMock, Mock
from http_client import HttpClient
from tests.async_mock import AsyncMock


@pytest.fixture()
def npsso():
    return "npsso"


@pytest.fixture()
def stored_credentials(npsso):
    return {"cookies": {"npsso": npsso}}


@pytest.fixture()
def account_id():
    return "accountId"


@pytest.fixture()
def online_id():
    return "onlineId"


@pytest.fixture()
def user_profile(online_id, account_id):
    return {
        "data": {
            "oracleUserProfileRetrieve": {
                "__typename": "ProfileOracle",
                "accountId": account_id,
                "age": 30,
                "avatar": {"__typename": "Media",
                          "url": "https://static-resource.np.community.playstation.net/avatar_xl/default/Defaultavatar_xl.png"},
                "hashedAccountId": "HASHED_ID",
                "isOfficiallyVerified": False,
                "isPsPlusMember": True,
                "locale": "pl-PL",
                "name": "NAME",
                "onlineId": online_id,
                "profilePicture": {"__typename": "Media",
                                  "url": "https://static-resource.np.community.playstation.net/avatar_xl/default/Defaultavatar_xl.png"},
                "subscriptionState": [
                    {"__typename": "Subscription", "subscriptionStatus": "SUBSCRIBED", "subscriptionType": "PSPLUS"},
                    {"__typename": "Subscription", "subscriptionStatus": "NEVER", "subscriptionType": "PSNOW"},
                    {"__typename": "Subscription", "subscriptionStatus": "NEVER", "subscriptionType": "EAACCESS"}
                ]
            }
        }
    }


@pytest.fixture()
def http_get(mocker):
    return mocker.patch(
        "plugin.HttpClient.get",
        new_callable=AsyncMock
    )


@pytest.fixture()
async def psn_plugin():
    plugin = PSNPlugin(MagicMock(), MagicMock(), None)
    yield plugin

    await plugin.shutdown()


@pytest.fixture()
@pytest.mark.asyncio
async def authenticated_plugin(
    psn_plugin,
    stored_credentials,
    account_id,
    online_id,
    mocker
):
    mocker.patch.object(PSNClient, "async_get_own_user_info", return_value=(account_id, online_id), new_callable=AsyncMock)

    await psn_plugin.authenticate(stored_credentials)
    return psn_plugin


@pytest.mark.asyncio
@pytest.fixture()
async def authenticated_psn_client():
    http_client = HttpClient()
    yield PSNClient(http_client=http_client)
    await http_client.close()


@pytest.fixture()
def mock_psn_client():
    psn_client = MagicMock()
    psn_client.async_get_own_user_info.return_value = async_return_value((Mock(str), Mock(str)))
    return psn_client


@pytest.fixture()
def create_plugin(mocker, mock_psn_client):
    async def inner():
        mocker.patch("plugin.PSNClient", return_value=mock_psn_client)
        async with PSNPlugin(MagicMock(), MagicMock(), None) as plugin:
            return plugin
    return inner
