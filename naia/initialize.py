from naia.auth.encryption import init_encryption


def initialize_app(
    encryption_key: str,
    default_salt: str,
) -> None:
    init_encryption(encryption_key, default_salt)
