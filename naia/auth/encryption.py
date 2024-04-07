from typing import Any, Optional, Union

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadSignature

_LEGACY_SALT: Optional[bytes]
_LEGACY_SERIALIZATION: URLSafeSerializer
_SYMMETRIC_ENCRYPTION: MultiFernet


def init_encryption(
    keys: list[str],
    legacy_key: str = '',
    legacy_salt: Optional[bytes] = b'',
) -> None:
    """Sets the serializer and default salt"""
    global _SYMMETRIC_ENCRYPTION, _LEGACY_SALT, _LEGACY_SERIALIZATION
    # Makes key rotations less of a lift - Key rotation would be a separate, deliberate action against the data store
    try:
        _SYMMETRIC_ENCRYPTION = MultiFernet([Fernet(k) for k in keys])
    except ValueError:
        pass

    # URLSafeSerializer has a default value for salt that we do not want to override unless a salt is specified
    if legacy_salt:
        _LEGACY_SERIALIZATION = URLSafeSerializer(secret_key=legacy_key, salt=legacy_salt)
        _LEGACY_SALT = legacy_salt
    else:
        _LEGACY_SERIALIZATION = URLSafeSerializer(secret_key=legacy_key)
        _LEGACY_SALT = _LEGACY_SERIALIZATION.salt


def decrypt(
    thing_to_decrypt: str,
) -> str:
    """Decrypts a string into the original object it was created from"""
    decrypted: str = ''
    try:
        decrypted = (_SYMMETRIC_ENCRYPTION.decrypt(thing_to_decrypt)).decode()
    except (AttributeError, NameError) as exc:
        print(f'init_encryption() must be called prior to decryption: {exc}')
    except InvalidToken as exc:
        print(f'Encryption.decrypt signature validation failed: {exc}')
    return decrypted


def legacy_verify(
    thing_to_decode: str,
    salt: Union[bytes, str] = '',
) -> Any:
    """Decode a signed string into the original object it was created from"""
    decoded: Any = ''
    try:
        decoded = _LEGACY_SERIALIZATION.loads(thing_to_decode, salt=salt or _LEGACY_SALT)
    except (AttributeError, NameError) as exc:
        print(f'init_encryption() must be called prior to decryption: {exc}')
    except BadSignature as exc:
        print(f'Encryption.decrypt signature validation failed: {exc}')
    return decoded
