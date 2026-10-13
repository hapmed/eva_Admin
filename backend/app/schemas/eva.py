"""Esquemas del catálogo EVA."""

from datetime import datetime

from pydantic import BaseModel, Field


class EvaCreate(BaseModel):
    code: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=500)
    config_schema: dict = Field(default_factory=dict)
    image_repo: str = Field(default="", max_length=200)
    container_port: int = Field(default=8000, ge=1, le=65535)
    healthcheck_path: str = Field(default="/healthz", max_length=120)
    migrate_command: str = Field(default="", max_length=300)


class EvaUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, pattern="^(active|deprecated)$")
    config_schema: dict | None = None
    image_repo: str | None = Field(default=None, max_length=200)
    container_port: int | None = Field(default=None, ge=1, le=65535)
    healthcheck_path: str | None = Field(default=None, max_length=120)
    migrate_command: str | None = Field(default=None, max_length=300)


class EvaVersionCreate(BaseModel):
    version: str = Field(min_length=1, max_length=40)
    status: str = Field(default="approved", pattern="^(approved|deprecated|blocked)$")
    deployment_requirements: dict = Field(default_factory=dict)


class EvaVersionOut(BaseModel):
    id: str
    version: str
    status: str
    deployment_requirements: dict
    created_at: datetime


class EvaOut(BaseModel):
    id: str
    code: str
    name: str
    description: str
    status: str
    config_schema: dict
    image_repo: str
    container_port: int
    healthcheck_path: str
    migrate_command: str
    versions: list[EvaVersionOut]
    created_at: datetime
