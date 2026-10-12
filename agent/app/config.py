"""Configuración del agente (variables de entorno, prefijo EVAS_)."""

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

    environment: str = "local"
    # Toggle explícito de seguridad: SIEMPRE arranca en simulado.
    agent_mode: str = Field(default="simulated", description="simulated | real")
    # Token compartido con el backend para autenticar la llamada. Ficticio.
    agent_token: str = ""
    # Sólo usado en modo real (no en Fase 2).
    docker_host: str = "unix:///var/run/docker.sock"
    managed_label: str = "evas.managed_by"
    eva_network: str = "apps-net"
    # Carpeta (montada del host) donde se guardan los respaldos.
    backup_dir: str = "/backups"
    postgres_container: str = "postgres"
    # Rutas del host montadas de solo lectura para métricas del servidor.
    host_proc: str = "/host/proc"
    host_root: str = "/host"

    @property
    def is_simulated(self) -> bool:
        return self.agent_mode != "real"


@lru_cache
def get_settings() -> Settings:
    return Settings()
