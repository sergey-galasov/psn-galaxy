import aiohttp
import logging

from urllib.parse import parse_qsl, urlsplit

from galaxy.api.errors import (
    AuthenticationRequired,
    BackendError,
    BackendNotAvailable,
    BackendTimeout,
    NetworkError,
    InvalidCredentials,
    UnknownBackendResponse
)
from galaxy.http import handle_exception, create_client_session


OAUTH_LOGIN_REDIRECT_URL = "https://my.playstation.com/auth/response.html"

# TODO: we probably do not need all these scopes
# TODO: generate random request ID
OAUTH_URL_BASE = \
    "https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/authorize" \
    "?response_type=token" \
    "&scope=capone:report_submission" \
        ",kamaji:game_list" \
        ",kamaji:get_account_hash" \
        ",user:account.get" \
        ",user:account.profile.get" \
        ",kamaji:social_get_graph" \
        ",kamaji:ugc:distributor" \
        ",user:account.identityMapper" \
        ",kamaji:music_views" \
        ",kamaji:activity_feed_get_feed_privacy" \
        ",kamaji:activity_feed_get_news_feed" \
        ",kamaji:activity_feed_submit_feed_story" \
        ",kamaji:activity_feed_internal_feed_submit_story" \
        ",kamaji:account_link_token_web" \
        ",kamaji:ugc:distributor_web" \
        ",kamaji:url_preview" \
    "&client_id=656ace0b-d627-47e6-915c-13b259cd06b2" \
    "&redirect_uri=" + OAUTH_LOGIN_REDIRECT_URL

OAUTH_LOGIN_URL = OAUTH_URL_BASE + "?requestID=external_request_e0002664-7e12-474b-ba44-495683d32d3c" \
    "&baseUrl=/" \
    "&returnRoute=/" \
    "&targetOrigin=https://my.playstation.com" \
    "&excludeQueryParams=true" \
    "&prompt=login" \
    "&tp_console=true" \
    "&ui=pr"

OAUTH_TOKEN_URL = OAUTH_URL_BASE + "?requestID=iframe_request_c37ac45d-d6f2-4585-b93f-da014fe87579" \
    "&baseUrl=/" \
    "&targetOrigin=https://my.playstation.com" \
    "&prompt=none"

DEFAULT_TIMEOUT = 30


def paginate_url(url, limit, offset=0):
    return url + "&limit={limit}&offset={offset}".format(limit=limit, offset=offset)


class AuthenticatedHttpClient:
    def __init__(self, auth_lost_callback):
        self._access_token = None
        self._refresh_token = None
        self._auth_lost_callback = auth_lost_callback
        self._session = create_client_session(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT))

    @property
    def is_authenticated(self):
        return self._access_token is not None

    def _auth_lost(self):
        self._access_token = None
        self._refresh_token = None
        if self._auth_lost_callback:
            self._auth_lost_callback()

    def _validate_auth_response(self, location_params):
        location_query = dict(parse_qsl(location_params.query))
        if "error" in location_query:
            raise AuthenticationRequired(location_query)

    async def get_access_token(self, refresh_token):
        response = None
        try:
            response = await self._request(
                "GET",
                url=OAUTH_TOKEN_URL,
                cookies={"npsso": refresh_token},
                allow_redirects=False
            )
            location_params = urlsplit(response.headers["Location"])
            self._validate_auth_response(location_params)
            return dict(parse_qsl(location_params.fragment))["access_token"]
        except AuthenticationRequired as e:
            raise InvalidCredentials(e.data)
        except (KeyError, IndexError):
            raise UnknownBackendResponse(str(response.headers))
        finally:
            if response:
                response.close()

    async def authenticate(self, refresh_token):
        self._refresh_token = refresh_token
        self._access_token = await self.get_access_token(self._refresh_token)
        if not self._access_token:
            raise UnknownBackendResponse("Empty access token")

    async def _refresh_access_token(self):
        try:
            self._access_token = await self.get_access_token(self._refresh_token)
            if not self._access_token:
                raise UnknownBackendResponse("Empty access token")
        except (BackendNotAvailable, BackendTimeout, BackendError, NetworkError):
            logging.warning("Failed to refresh token for independent reasons")
            raise
        except Exception:
            logging.exception("Failed to refresh token")
            if self._auth_lost_callback:
                self._auth_lost_callback()
            raise AuthenticationRequired()

    async def request(self, method, *args, **kwargs):
        if not self._access_token:
            raise AuthenticationRequired()

        try:
            return await self._oauth_request(method, *args, **kwargs)
        except AuthenticationRequired:
            await self._refresh_access_token()
            return await self._oauth_request(method, *args, **kwargs)

    async def _oauth_request(self, method, *args, **kwargs):
        headers = kwargs.setdefault("headers", {})
        headers["authorization"] = "Bearer " + self._access_token
        return await self._request(method, *args, **kwargs)

    async def _request(self, method, *args, **kwargs):
        with handle_exception():
            return await self._session.request(method, *args, **kwargs)

    async def get(self, url, *args, **kwargs):
        response = await self.request("GET", *args, url=url, **kwargs)
        try:
            logging.debug("Response for:\n{url}\n{data}".format(url=url, data=await response.text()))
            return await response.json()
        except ValueError:
            logging.exception("Invalid response data for:\n{url}".format(url=url))
            raise UnknownBackendResponse()

    async def post(self, url, *args, **kwargs):
        logging.debug("Sending data:\n{url}".format(url=url))
        return await self.request("POST", *args, url=url, **kwargs)

    async def logout(self):
        await self._session.close()
