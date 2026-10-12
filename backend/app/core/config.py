"""Configuración centralizada (variables de entorno, prefijo EVAS_).

No contiene secretos reales: los valores por defecto son ficticios y sirven de
ejemplo. Los valores reales llegan por entorno o gestor de secretos.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EVAS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EVAS Admin API"
    environment: str = Field(default="local", description="local | test | staging | prod")
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Base administrativa (instancia PostgreSQL existente). Fase 2 NO conecta.
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "evas_admin"
    db_user: str = "evas_admin_app"
    db_password: str = "change-me-in-env"
    db_sslmode: str = "prefer"

    # Sesión web (cookie)
    session_cookie_name: str = "evas_session"
    session_cookie_secure: bool = True
    session_cookie_samesite: str = "lax"

    # CORS: orígenes permitidos (vacío = ninguno).
    cors_origins: list[str] = Field(default_factory=list)

    # Agente de operaciones
    agent_mode: str = Field(default="simulated", description="simulated | real")

    @property
    def database_url(self) -> str:
        """DSN de la base administrativa. No se usa en Fase 2."""
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_sslmode}"
        )

    @property
    def is_local(self) -> bool:
        return self.environment in {"local", "test"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
