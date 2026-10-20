"""Esquemas de instalaciones, dominios, bases de datos y operaciones."""

from datetime import datetime

from pydantic import BaseModel, Field


class NodeOut(BaseModel):
    id: str
    name: str
    host_ref: str
    environment: str
    status: str


class SecretRefIn(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    provider: str = Field(default="env", max_length=60)
    path: str = Field(default="", max_length=200)


class SecretRefOut(BaseModel):
    key: str
    provider: str


class InstallationServiceOut(BaseModel):
    id: str
    service_name: str
    container_ref: str
    image_ref: str
    status: str
    health_status: str
    last_checked_at: datetime | None


class InstallationCreate(BaseModel):
    client_id: str
    eva_product_id: str
    subscription_id: str | None = None
    node_id: str | None = None
    environment: str = Field(default="prod", pattern="^(prod|staging|local)$")
    desired_version: str = Field(min_length=1, max_length=40)
    primary_domain: str | None = Field(default=None, max_length=253)
    config: dict = Field(default_factory=dict)
    secrets: list[SecretRefIn] = Field(default_factory=list)
    idempotency_key: str | None = Field(default=None, max_length=120)


class InstallationUpdate(BaseModel):
    environment: str | None = Field(default=None, pattern="^(prod|staging|local)$")
    desired_version: str | None = Field(default=None, max_length=40)


class InstallationOut(BaseModel):
    id: str
    client_id: str
    eva_product_id: str
    subscription_id: str | None
    node_id: str | None
    environment: str
    status: str
    desired_version: str
    installed_version: str | None
    last_operation_at: datetime | None
    host_port: int | None
    container_name: str
    services: list[InstallationServiceOut]
    domains: list[str]
    secrets: list[SecretRefOut]


class InstallationDeleteOut(BaseModel):
    id: str
    deleted: bool
    warnings: list[str] = Field(default_factory=list)


class OperationRequest(BaseModel):
    idempotency_key: str | None = Field(default=None, max_length=120)
    notes: str = Field(default="", max_length=300)


class UpgradeRequest(OperationRequest):
    target_version: str = Field(min_length=1, max_length=40)


class RestartRequest(OperationRequest):
    service_name: str = Field(min_length=1, max_length=80)


class OperationOut(BaseModel):
    id: str
    installation_id: str | None
    type: str
    status: str
    requested_at: datetime
    finished_at: datetime | None
    result_summary: str
    error_code: str | None
    simulated: bool


class DomainCreate(BaseModel):
    installation_id: str
    fqdn: str = Field(min_length=3, max_length=253)
    kind: str = Field(default="primary", pattern="^(primary|alias)$")


class DomainOut(BaseModel):
    id: str
    installation_id: str
    fqdn: str
    kind: str
    status: str


class DomainCheck(BaseModel):
    fqdn: str
    available: bool


class DatabaseCreate(BaseModel):
    installation_id: str
    engine: str = Field(default="postgresql", max_length=30)
    logical_name: str = Field(min_length=1, max_length=120)
    host_ref: str = Field(default="", max_length=160)


class DatabaseOut(BaseModel):
    id: str
    installation_id: str
    engine: str
    logical_name: str
    host_ref: str
    status: str
    last_backup_at: datetime | None


class RestoreRequest(OperationRequest):
    backup_ref: str = Field(min_length=1, max_length=200)
    confirm: str = Field(default="", max_length=120)


class BackupOut(BaseModel):
    id: str
    database_record_id: str
    type: str
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    location_ref: str | None
    size_bytes: int | None
