"""Common utilities and shared code"""

from src.common.auth import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from src.common.database import Base, get_db


def __getattr__(name):
    """Lazy load engine and SessionLocal to avoid circular imports"""
    if name == "engine":
        from src.common.database import get_engine

        return get_engine()
    elif name == "SessionLocal":
        from src.common.database import get_session_local

        return get_session_local()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "get_db",
    "engine",
    "SessionLocal",
    "Base",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
]
