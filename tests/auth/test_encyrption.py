from cryptography.fernet import Fernet
import pytest

from naia.auth.encryption import decrypt, init_encryption


def test_wb_init_encryption_valid_b64():
    # byte and string url_encoded are accepted
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    init_encryption(keys)


def test_wb_init_encryption_valid_legacy():
    # byte and string url_encoded are accepted
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    init_encryption(keys, b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=')


def test_ut_init_encryption_invalid_too_short():
    not_long_enough = [
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nw==',
    ]
    with pytest.raises(ValueError):
        init_encryption(not_long_enough)


def test_ut_init_encryption_invalid_not_url_encoded():
    not_url_encoded = [
        '&*?-'*8,
    ]
    with pytest.raises(ValueError):
        init_encryption(not_url_encoded)


def test_ut_init_encryption_invalid_not_iterable():
    # Valid key, but is not a list
    not_a_list = 'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY='
    with pytest.raises(TypeError) as exc:
        init_encryption(not_a_list)
    assert 'list' in str(exc)


def test_ut_init_encryption_invalid_legacy_type():
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    with pytest.raises(TypeError):
        init_encryption(keys, 1234)


def test_wb_valid_decrypt_first_key():
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    init_encryption(keys)
    # Encrypt using the key specified
    fk = Fernet(keys[0])
    test_str = 'primary key'
    enc_str = fk.encrypt(test_str.encode())
    assert decrypt(enc_str) == test_str

def test_wb_valid_decrypt_old_key():
    keys = [
        b'YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',
        'Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc=',
    ]
    init_encryption(keys)
    # Encrypt using the key specified
    fk = Fernet(keys[1])
    test_str = 'old key'
    enc_str = fk.encrypt(test_str.encode())
    assert decrypt(enc_str) == test_str

