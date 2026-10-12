"""Configuración centralizada (variables de entorno, prefijo EVAS_).

No contiene secretos reales: los valores por defecto son ficticios y sirven de
ejemplo. Los valores reales llegan por entorno o gestor de secretos.
"""

from functools import lru_cache
from typing import Literal

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

    # Base administrativa (instancia PostgreSQL existente).
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "evas_admin"
    db_user: str = "evas_admin_app"
    db_password: str = "change-me-in-env"
    db_sslmode: str = "prefer"

    # Sesión web (cookie firmada) y CSRF
    secret_key: str = "change-me-session-secret"
    session_cookie_name: str = "evas_session"
    csrf_cookie_name: str = "evas_csrf"
    session_ttl_minutes: int = 720
    session_cookie_secure: bool = True
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    # CORS: orígenes permitidos (vacío = ninguno).
    cors_origins: list[str] = Field(default_factory=list)

    # Rate limiting (rutas sensibles).
    rate_limit_enabled: bool = True
    rate_limit_auth_per_minute: int = 20
    rate_limit_operations_per_minute: int = 120

    # Agente de operaciones
    agent_mode: str = Field(default="simulated", description="simulated | real")
    agent_url: str = "http://agent:8001"
    agent_token: str = ""

    # WebAuthn / passkeys (RP ID por dominio del host; override opcional)
    webauthn_rp_name: str = "EVAS Admin"
    webauthn_rp_id: str = ""

    # Notificaciones por email (SMTP). Deshabilitado por defecto; rellenar en prod.
    smtp_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "evas-admin@hapmed.local"
    smtp_to: list[str] = Field(default_factory=list)
    smtp_starttls: bool = True
    smtp_ssl: bool = False

    # Aprovisionamiento real (bases de datos por cliente, contenedores, DNS).
    provision_enabled: bool = False
    provision_db_host: str = "postgres"
    provision_db_port: int = 5432
    provision_db_admin_user: str = ""
    provision_db_admin_password: str = ""
    provision_db_admin_db: str = "postgres"
    provision_user_prefix: str = "eva"
    port_range_start: int = 9100
    port_range_end: int = 9199
    eva_network: str = "apps-net"
    # Cloudflare (túnel + DNS) para publicar el dominio del cliente.
    public_domain_suffix: str = "hapmed.qzz.io"
    cloudflare_api_token: str = ""
    cloudflare_account_id: str = ""
    cloudflare_zone_id: str = ""
    cloudflare_tunnel_id: str = ""

    # Administrador inicial (bootstrap). Sólo se usa para crear el primer usuario.
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""

    @property
    def database_url(self) -> str:
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
