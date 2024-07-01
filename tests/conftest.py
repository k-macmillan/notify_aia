import datetime
from typing import Any, Callable, Generator, Tuple
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from itsdangerous import URLSafeSerializer

from naia import Naia
from naia.clients.callback.rest import RequestPayload


@pytest.fixture()
def get_app() -> Naia:
    return Naia()


@pytest.fixture()
def enc_key() -> Tuple[str]:
    return ('YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',)


@pytest.fixture()
def encrypted_str(enc_key: Tuple[str]) -> Generator[Callable[[str], str], Any, Any]:
    fk = Fernet(enc_key[0])

    def _wrapper(str_to_encrypt: str = 'test str') -> str:
        return fk.encrypt(str_to_encrypt.encode()).decode()

    yield _wrapper


@pytest.fixture()
def legacy_verify_str(enc_key: Tuple[str]) -> Generator[Callable[[str], str], Any, Any]:
    legacy_verify = URLSafeSerializer(enc_key[0])

    def _wrapper(str_to_encrypt: str = 'test str') -> str:
        return legacy_verify.dumps(str_to_encrypt)

    yield _wrapper


@pytest.fixture()
def delivered_payload() -> RequestPayload:
    return RequestPayload(
        notification_id=uuid4(),
        to='Smash Mouth',
        status='delivered',
        created_at=datetime.datetime.now(datetime.UTC),
        completed_at=datetime.datetime.now(datetime.UTC),
        sent_at=datetime.datetime.now(datetime.UTC),
        notification_type='sms',
    )
