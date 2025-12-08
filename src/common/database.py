"""Database connection and session management"""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

_engine = None
_SessionLocal = None


def _get_database_url():
    """Get database URL from settings or environment"""
    # Try environment variable first (for tests)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    # Otherwise import settings (lazy import to avoid circular dependency)
    from src.api.config import settings

    return settings.DATABASE_URL


def get_engine():
    """Get or create database engine (lazy initialization)"""
    global _engine
    if _engine is None:
        _engine = create_engine(_get_database_url(), pool_pre_ping=True)
    return _engine


def get_session_local():
    """Get or create session factory (lazy initialization)"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """Database session dependency"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# For backward compatibility - access via __getattr__ for lazy loading
def __getattr__(name):
    if name == "engine":
        return get_engine()
    elif name == "SessionLocal":
        return get_session_local()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
