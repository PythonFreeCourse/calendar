"""Temp file to prevent file conflicts while WiP."""
from pydantic import SecretStr

from app.internal.security.ouath2 import pwd_context


def get_hashed_password_v2(password: SecretStr) -> str:
    """Hashes the user's password.

    Args:
        password: An unhashed password.

    Returns:
        A hashed password.
    """
    unhashed_password = password.get_secret_value().encode("utf-8")
    return pwd_context.hash(unhashed_password)
