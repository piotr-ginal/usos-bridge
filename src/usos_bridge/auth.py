from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup as Bs


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
