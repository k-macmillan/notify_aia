from typing import Any, Iterable, Optional, Union

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadSignature

t_byte_str = Union[bytes, str]
t_legacy_secret_key = Union[Iterable[t_byte_str], t_byte_str]

_LEGACY_SALT: Optional[t_byte_str]
_LEGACY_SERIALIZATION: URLSafeSerializer
_SYMMETRIC_ENCRYPTION: MultiFernet


def init_encryption(
    b64_keys: list[t_byte_str],
    legacy_key: Optional[t_legacy_secret_key] = '',
    legacy_salt: Optional[t_byte_str] = b'itsdangerous',
) -> None:
    """Initializes 32 byte Fernet keys for encryption and sets the serializer and default salt if applicable"""
    global _SYMMETRIC_ENCRYPTION, _LEGACY_SALT, _LEGACY_SERIALIZATION
    # Makes key rotations less of a lift - Key rotation would be a separate, deliberate action against the data store
    try:
        _SYMMETRIC_ENCRYPTION = MultiFernet([Fernet(k) for k in b64_keys])
    except ValueError as exc:
        if any([k for k in b64_keys if len(k) < 32]):
            print('Keys must be 32 bytes')
        # TODO: Version 2.0 begin using this warning, 3.0 remove it
        # import warnings
        # warnings.warn(
        #     "Legacy salt/key are kept for backwards compatibility and will be deprecated in a future version",
        #     DeprecationWarning,
        # )
        print(f'Not using encryption - decrypt method unavailable: {exc}')

    if legacy_key:
        _LEGACY_SERIALIZATION = URLSafeSerializer(secret_key=legacy_key, salt=legacy_salt)
        _LEGACY_SALT = legacy_salt


def decrypt(
    thing_to_decrypt: str,
) -> str:
    """Decrypts a string into the original object it was created from"""
    decrypted: str = ''
    try:
        decrypted = (_SYMMETRIC_ENCRYPTION.decrypt(thing_to_decrypt)).decode()
    except (AttributeError, NameError) as exc:
        print(f'init_encryption() must be called with `keys` set prior to decryption: {exc}')
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
