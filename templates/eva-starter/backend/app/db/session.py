"""Sesión de base de datos.

El engine se crea de forma perezosa: importar este módulo no abre conexiones ni
requiere el driver de PostgreSQL. Fase 2 no ejecuta consultas.
"""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True, future=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Dependencia FastAPI. No se usa en Fase 2."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
