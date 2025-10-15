# ruff: noqa: INP001
import os
import sys

from dotenv import load_dotenv

from usos_bridge.auth import WebUsosAuthenticator
from usos_bridge.client import UsosApiClient
from usos_bridge.instance_config import load_instance_configs


def main() -> None:

    load_dotenv()

    login = os.getenv("USOS_LOGIN")
    password = os.getenv("USOS_PASSWORD")

    if login is None or password is None:
        raise RuntimeError

    config = load_instance_configs()["pwr"]
    authenticator = WebUsosAuthenticator(login, password, config)
    client = UsosApiClient(config, authenticator)

    response = client.request("services/users/user")  # https://apps.usos.edu.pl/developers/api/services/users/#user

    sys.stdout.write(response.text + "\n")


if __name__ == "__main__":
    main()
