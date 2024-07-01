"""Naia encryption module."""

from typing import Any, Iterable, Optional, Union

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadSignature

t_bytes_str = Union[bytes, str]
t_secret_key = Union[t_bytes_str, Iterable[bytes], Iterable[str]]

_LEGACY_SALT: Optional[t_bytes_str]
_LEGACY_SERIALIZATION: URLSafeSerializer
_SYMMETRIC_ENCRYPTION: MultiFernet


def init_encryption(
    b64_keys: Iterable[t_bytes_str],
    legacy_key: Optional[t_secret_key] = '',
    legacy_salt: Optional[t_bytes_str] = b'itsdangerous',
) -> None:
    """
    Initialize 32 byte Fernet keys for encryption and sets the serializer and default salt if applicable.

    Args:
    ----
        b64_keys: Iterable[t_bytes_str]
            url-safe encoded string or bytestring used for encryption
        legacy_key: Optional[t_secret_key]
            key or keys for signing
        legacy_salt: Optional[t_bytes_str]
            salt used for signing

    """
    global _SYMMETRIC_ENCRYPTION, _LEGACY_SALT, _LEGACY_SERIALIZATION
    # Makes key rotations less of a lift - Key rotation would be a separate, deliberate action against the data store
    _SYMMETRIC_ENCRYPTION = MultiFernet([Fernet(k) for k in b64_keys])

    if legacy_key:
        _LEGACY_SERIALIZATION = URLSafeSerializer(secret_key=legacy_key, salt=legacy_salt)
        _LEGACY_SALT = legacy_salt


def decrypt(
    thing_to_decrypt: t_bytes_str,
) -> str:
    """
    Decrypts a string into the original object it was created from.

    Args:
    ----
        thing_to_decrypt: t_bytes_str
            The object to be decrypted

    Returns:
    -------
        str: The decrypted string

    """
    decrypted: str = ''
    try:
        decrypted = (_SYMMETRIC_ENCRYPTION.decrypt(thing_to_decrypt)).decode()
    except (AttributeError, NameError) as exc:
        raise RuntimeError(f'init_encryption() must be called with `keys` set prior to decryption: {exc}')
    except InvalidToken as exc:
        raise ValueError(f'Encryption.decrypt signature validation failed: {exc}')
    return decrypted


def legacy_verify(
    thing_to_decode: t_bytes_str,
    salt: t_bytes_str = b'',
) -> Any:
    """
    Decode a signed string into the original object it was created from.

    This is only signing, no encryption

    Args:
    ----
        thing_to_decode: t_bytes_str
            The object to be decrypted
        salt: t_bytes_str
            The salt to use during this validation

    Returns:
    -------
        Any: The verfiied object

    """
    decoded: Any = ''
    try:
        decoded = _LEGACY_SERIALIZATION.loads(thing_to_decode, salt=salt or _LEGACY_SALT)
    except (AttributeError, NameError) as exc:
        raise RuntimeError(f'init_encryption() must be called prior to decryption: {exc}')
    except BadSignature as exc:
        raise ValueError(f'Encryption.decrypt signature validation failed: {exc}')
    return decoded
