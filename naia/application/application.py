from typing import Any

from naia import Naia
from naia.auth.encryption import init_encryption

app: Naia


def initialize_app(application: Naia, encryption: dict[str, Any]) -> None:
    global app
    app = application
    init_encryption(**encryption)
