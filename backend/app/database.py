from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _database_url() -> str | None:
    if not settings.database_url:
        return None
    if settings.database_url.startswith("postgres://"):
        return settings.database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if settings.database_url.startswith("postgresql://"):
        return settings.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return settings.database_url


def _engine_options(database_url: str) -> dict:
    options: dict = {"pool_pre_ping": True}
    if database_url.startswith("postgresql+psycopg://"):
        options["connect_args"] = {"connect_timeout": 5}
    return options


DATABASE_URL = _database_url()
engine = create_engine(DATABASE_URL, **_engine_options(DATABASE_URL)) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None
_database_enabled = engine is not None


def database_available() -> bool:
    return SessionLocal is not None and _database_enabled


def disable_database() -> None:
    global _database_enabled
    _database_enabled = False


def init_db() -> None:
    if engine is None:
        return
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        disable_database()
        print(f"Warning: database unavailable, falling back to local JSON storage. {exc.__class__.__name__}")


def get_session() -> Generator[Session, None, None]:
    if not database_available():
        raise RuntimeError("Database is not configured or is unavailable.")
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
