# USOS Bridge

Use your web usos credentials to interact with the USOS API

-----

## Installation

Install the package directly from PyPI:

```bash
pip install usos-bridge
```

-----

## Usage

Simplest example (for pwr)
```python
from usos_bridge.auth import WebUsosAuthenticator
from usos_bridge.client import UsosApiClient
from usos_bridge.instance_config import load_instance_configs


config = load_instance_configs()["pwr"]
authenticator = WebUsosAuthenticator("usos web login", "usos web password", config)
client = UsosApiClient(config, authenticator)

response = client.request("services/users/user", {"fields": "id"})
```

A complete list of USOS instances and links to their official API documentation is available on the [USOS Apps Developer Page](https://apps.usos.edu.pl/developers/api/definitions/installations/).

If your instance isn't listed, contributions are highly welcome. Feel free to open a pull request to add support yourself. You can also open an issue with your university's name, and I will do my best to add it. Please note that this will require us to work together, as I'll need your help with testing since I don't have access to your university's system.

-----

## Development

1. Clone this repository
2. Install development dependencies:

```bash
pip install -e .
pip install -r ./requirements/dev.txt
pre-commit install
```

-----

## License

This project is licensed under the MIT License - see the LICENSE file for details.
