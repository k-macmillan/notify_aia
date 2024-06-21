from typing import Tuple

import pytest

from naia import Naia


@pytest.fixture()
def get_app() -> Naia:
    return Naia()


@pytest.fixture()
def enc_key() -> Tuple[str]:
    return ('YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',)
