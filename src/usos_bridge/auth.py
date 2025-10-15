from typing import NamedTuple
from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup as Bs

MAX_AUTH_RETRY: int = 4


class AuthPair(NamedTuple):
    cookie: str
    csrf_token: str


def _construct_auth_page_url() -> str:
    usos_web_auth_url: str = "https://login.pwr.edu.pl/auth/realms/pwr.edu.pl/protocol/cas/login"
    service_param_value: str = "https://web.usos.pwr.edu.pl/kontroler.php?_action=logowaniecas/index"

    params = {
        "service": service_param_value,
        "locale": "pl",
    }

    service_param_value_encoded: str = urlencode(params)

    return f"{usos_web_auth_url}?{service_param_value_encoded}"


def _get_login_endpoint_url(auth_page_url: str, client: httpx.Client) -> str:
    response = client.get(auth_page_url)

    response.raise_for_status()

    auth_page = Bs(response.text, "html.parser")

    login_form = auth_page.select_one("form.login-form")

    if login_form is None:
        msg = "No login form found"
        raise RuntimeError(msg)  # TODO(ginal): custom error

    auth_url = login_form.attrs.get("action")

    if auth_url is not None:
        return auth_url

    msg = "Auth url in login form not found"
    raise RuntimeError(msg)  # TODO(ginal): custom error


def _authorize_client(username: str, password: str, client: httpx.Client) -> None:
    auth_page_url = _construct_auth_page_url()
    auth_endpoint = _get_login_endpoint_url(auth_page_url, client)

    client.post(
        auth_endpoint,
        data={"username": username, "password": password},
        follow_redirects=True,
    )

    if client.cookies.get("PHPSESSID") is None:
        raise RuntimeError  # TODO(ginal): custom error here


def get_auth_pair(username: str, password: str) -> AuthPair:
    with httpx.Client() as client:
        _authorize_client(username, password, client)
        cookies: httpx.Cookies = client.cookies

    return AuthPair(cookies["PHPSESSID"], "")


class WebUsosAuthenticator:
    def __init__(self, username: str, password: str) -> None:
        self._username: str = username
        self._password: str = password

        self._auth_pair: AuthPair | None = None

    def _ensure_valid_auth_pair(self, *, retry: int = 1) -> AuthPair:
        if retry > MAX_AUTH_RETRY:
            raise RuntimeError  # TODO(ginal): implement custom error

        try:
            self._auth_pair = get_auth_pair(self._username, self._password)
        except Exception:  # noqa: BLE001 TODO(ginal): catch possible errors here
            return self._ensure_valid_auth_pair(retry=retry + 1)

        return self._auth_pair

    def refresh(self) -> None:
        self._ensure_valid_auth_pair()

    @property
    def cookie(self) -> str:
        if self._auth_pair is None:
            return self._ensure_valid_auth_pair().cookie

        return self._auth_pair.cookie

    @property
    def csrf_token(self) -> str:
        if self._auth_pair is None:
            return self._ensure_valid_auth_pair().csrf_token

        return self._auth_pair.csrf_token
