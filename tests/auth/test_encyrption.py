from typing import Iterable

import pytest
from cryptography.fernet import Fernet
from itsdangerous import URLSafeSerializer

import notify_aia.auth.encryption as naia_encr

default_keys = [
    'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
    'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
]


@pytest.mark.parametrize(
    'bytes_keys',
    [
        [
            b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
            b'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
        ],
        (
            b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
            b'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
        ),
        {
            b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
            b'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
        },
    ],
)
def test_wb_init_encryption_valid_bytes_b64(bytes_keys: Iterable[bytes]) -> None:
    naia_encr.init_encryption(bytes_keys)


@pytest.mark.parametrize(
    'str_keys',
    [
        [
            'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
            'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
        ],
        (
            'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
            'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
        ),
        {
            'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
            'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
        },
    ],
)
def test_wb_init_encryption_valid_str_b64(str_keys: Iterable[str]) -> None:
    naia_encr.init_encryption(str_keys)


def test_wb_init_encryption_valid_legacy() -> None:
    # byte and string url_encoded are accepted
    naia_encr.init_encryption(default_keys, b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=')
    naia_encr.init_encryption(default_keys, 'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=')


def test_ut_init_encryption_invalid_too_short() -> None:
    not_long_enough = [
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nw==',
    ]
    with pytest.raises(ValueError):
        naia_encr.init_encryption(not_long_enough)


def test_ut_init_encryption_invalid_not_url_encoded() -> None:
    not_url_encoded = [
        '&*?-' * 8,
    ]
    with pytest.raises(ValueError):
        naia_encr.init_encryption(not_url_encoded)


def test_ut_init_encryption_invalid_not_iterable() -> None:
    with pytest.raises(TypeError, match='not iterable'):
        # Ignoring mypy error to ensure this is handled
        naia_encr.init_encryption(777)  # type: ignore


def test_wb_valid_decrypt_first_key() -> None:
    naia_encr.init_encryption(default_keys)
    # Encrypt using the key specified
    fk = Fernet(default_keys[0])
    test_str = 'primary key'
    enc_str = fk.encrypt(test_str.encode())
    assert naia_encr.decrypt(enc_str) == test_str


def test_wb_valid_decrypt_old_key() -> None:
    naia_encr.init_encryption(default_keys)
    # Encrypt using the key specified
    fk = Fernet(default_keys[1])
    test_str = 'old key'
    enc_str = fk.encrypt(test_str.encode())
    assert naia_encr.decrypt(enc_str) == test_str


def test_ut_decrypt_with_missing_b64key() -> None:
    # Set it to None for the test since it's a module-level object - ignore mypy
    naia_encr._SYMMETRIC_ENCRYPTION = None  # type: ignore
    with pytest.raises(RuntimeError, match='init_encryption'):
        naia_encr.decrypt('test')


def test_ut_decrypt_with_invalid_b64key() -> None:
    old_key = b'ZjbHlxX4XyYDvmwuEMozeGeq05xOuzv2QJ9qrII7Lk4='
    fk = Fernet(old_key)
    enc_str = fk.encrypt('old key'.encode())

    naia_encr.init_encryption(default_keys)
    with pytest.raises(ValueError, match='validation failed'):
        naia_encr.decrypt(enc_str)


def test_wb_valid_legacy_key() -> None:
    legacy_key = [
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    naia_encr.init_encryption(b64_keys=default_keys, legacy_key=legacy_key)
    serializer = URLSafeSerializer(secret_key=legacy_key)
    test_str = 'The way to get started is to quit talking and begin doing'
    signed = serializer.dumps(test_str)
    assert naia_encr.legacy_verify(signed) == test_str


def test_wb_valid_legacy_old_key() -> None:
    legacy_key = 'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc='
    # Test with one of the legacy keys removed
    naia_encr.init_encryption(b64_keys=default_keys, legacy_key=default_keys)
    # Representing a past init_encryption with both keys in use
    serializer = URLSafeSerializer(secret_key=legacy_key)
    test_str = 'Well done is better than well said'
    signed = serializer.dumps(test_str)
    assert naia_encr.legacy_verify(signed) == test_str


def test_ut_missing_legacy_key_for_legacy_verify() -> None:
    naia_encr.init_encryption(b64_keys=default_keys)
    # Set it to None for the test since it's a module-level object - ignore mypy
    naia_encr._LEGACY_SERIALIZATION = None  # type: ignore

    with pytest.raises(RuntimeError, match='init_encryption'):
        naia_encr.legacy_verify('')


def test_ut_legacy_verify_invalid_signature() -> None:
    key = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
    ]
    # Setup as if it was signed with a different key
    old_key = 'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc='
    serializer = URLSafeSerializer(secret_key=old_key)
    signed = serializer.dumps('Life is a succession of lessons which must be lived to be understood')

    naia_encr.init_encryption(b64_keys=key, legacy_key=key)
    with pytest.raises(ValueError, match='validation failed'):
        naia_encr.legacy_verify(signed)
