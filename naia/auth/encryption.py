from typing import Any

from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadSignature

_SERIALIZATION: URLSafeSerializer
_SALT: str


def init_encryption(
    key: str,
    salt: str,
) -> None:
    """Sets the serializer and default salt"""
    global _SERIALIZATION, _SALT
    _SERIALIZATION = URLSafeSerializer(key, salt)
    _SALT = salt


def decrypt(
    thing_to_decrypt: str,
    salt: str = '',
) -> Any:
    """Decrypts a string into the original object it was created from"""
    try:
        return _SERIALIZATION.loads(thing_to_decrypt, salt=salt or _SALT)
    except (AttributeError, NameError) as exc:
        raise RuntimeError(f'init_encryption() must be called prior to decryption: {exc}')
    except BadSignature as exc:
        raise RuntimeError(f'Encryption.decrypt signature validation failed: {exc}')
