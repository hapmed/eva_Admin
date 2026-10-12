"""Configuración centralizada (variables de entorno).

Prefijo `EVA_` para lo propio de la app y alias para las variables que inyecta
la plataforma EVAS Admin (`DATABASE_URL`, `EVAS_*`). Sin secretos por defecto.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EVA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EVA Starter"
    environment: str = "local"
    debug: bool = False

    # Branding (rebrandable por cliente sin tocar código).
    client_name: str = Field(default="HAPMED", alias="EVA_CLIENT_NAME")

    # Inyectadas por la plataforma EVAS Admin.
    version: str = Field(default="dev", alias="EVAS_VERSION")
    eva_code: str = Field(default="", alias="EVAS_EVA_CODE")
    installation_id: str = Field(default="", alias="EVAS_INSTALLATION_ID")
    client_ref: str = Field(default="", alias="EVAS_CLIENT_REF")
    database_url: str = Field(
        default="postgresql+psycopg://eva:eva@localhost:5432/eva",
        alias="DATABASE_URL",
    )

    @property
    def is_local(self) -> bool:
        return self.environment in {"local", "test"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
