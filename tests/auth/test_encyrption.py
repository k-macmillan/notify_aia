import pytest
from cryptography.fernet import Fernet
from itsdangerous import URLSafeSerializer

import naia.auth.encryption as naia_encr


def test_wb_init_encryption_valid_b64():
    # byte and string url_encoded are accepted
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    naia_encr.init_encryption(keys)


def test_wb_init_encryption_valid_legacy():
    # byte and string url_encoded are accepted
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    naia_encr.init_encryption(keys, b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=')


def test_ut_init_encryption_invalid_too_short():
    not_long_enough = [
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nw==',
    ]
    with pytest.raises(ValueError):
        naia_encr.init_encryption(not_long_enough)


def test_ut_init_encryption_invalid_not_url_encoded():
    not_url_encoded = [
        '&*?-' * 8,
    ]
    with pytest.raises(ValueError):
        naia_encr.init_encryption(not_url_encoded)


def test_ut_init_encryption_invalid_not_iterable():
    # Valid key, but is not a list
    not_a_list = 'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY='
    with pytest.raises(TypeError) as exc:
        naia_encr.init_encryption(not_a_list)
    assert 'list' in str(exc)


def test_ut_init_encryption_invalid_legacy_type():
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    with pytest.raises(TypeError):
        naia_encr.init_encryption(keys, 1234)


def test_wb_valid_decrypt_first_key():
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    naia_encr.init_encryption(keys)
    # Encrypt using the key specified
    fk = Fernet(keys[0])
    test_str = 'primary key'
    enc_str = fk.encrypt(test_str.encode())
    assert naia_encr.decrypt(enc_str) == test_str


def test_wb_valid_decrypt_old_key():
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    naia_encr.init_encryption(keys)
    # Encrypt using the key specified
    fk = Fernet(keys[1])
    test_str = 'old key'
    enc_str = fk.encrypt(test_str.encode())
    assert naia_encr.decrypt(enc_str) == test_str


def test_ut_decrypt_with_missing_b64key():
    naia_encr._SYMMETRIC_ENCRYPTION = None
    with pytest.raises(RuntimeError) as exc:
        naia_encr.decrypt('test')
    assert 'init_encryption' in str(exc)


def test_ut_decrypt_with_invalid_b64key():
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    old_key = b'ZjbHlxX4XyYDvmwuEMozeGeq05xOuzv2QJ9qrII7Lk4='
    fk = Fernet(old_key)
    enc_str = fk.encrypt('old key'.encode())

    naia_encr.init_encryption(keys)
    with pytest.raises(ValueError) as exc:
        naia_encr.decrypt(enc_str)
    # Ensure user understands the validation failed
    assert 'validation failed' in str(exc)



def test_wb_valid_legacy_key():
    key = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
    ]
    legacy_key = [
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    naia_encr.init_encryption(b64_keys=key, legacy_key=legacy_key)
    serializer = URLSafeSerializer(secret_key=legacy_key)
    test_str = 'The way to get started is to quit talking and begin doing'
    signed = serializer.dumps(test_str)
    assert naia_encr.legacy_verify(signed) == test_str


def test_wb_valid_legacy_old_key():
    key = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
    ]
    legacy_keys = [
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
    ]
    # Test with one of the legacy keys removed
    naia_encr.init_encryption(b64_keys=key, legacy_key=key)
    # Representing a past init_encryption with both keys in use
    serializer = URLSafeSerializer(secret_key=legacy_keys)
    test_str = 'Well done is better than well said'
    signed = serializer.dumps(test_str)
    assert naia_encr.legacy_verify(signed) == test_str


def test_ut_missing_legacy_key_for_legacy_verify(module_mocker):
    key = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
    ]
    naia_encr.init_encryption(b64_keys=key)
    # Have to unset this due to other tests setting it
    naia_encr._LEGACY_SERIALIZATION = None

    with pytest.raises(RuntimeError) as exc:
        naia_encr.legacy_verify('')
    # Ensure user is pointed to init_encryption
    assert 'init_encryption' in str(exc)


def test_ut_legacy_verify_invalid_signature():
    key = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
    ]
    # Setup as if it was signed with a different key
    old_key = 'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc='
    serializer = URLSafeSerializer(secret_key=old_key)
    signed = serializer.dumps('Life is a succession of lessons which must be lived to be understood')

    naia_encr.init_encryption(b64_keys=key, legacy_key=key)
    with pytest.raises(ValueError) as exc:
        naia_encr.legacy_verify(signed)
    # Ensure user understands the validation failed
    assert 'validation failed' in str(exc)
