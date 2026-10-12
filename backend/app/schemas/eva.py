"""Esquemas del catálogo EVA."""

from datetime import datetime

from pydantic import BaseModel, Field


class EvaCreate(BaseModel):
    code: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=500)


class EvaUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, pattern="^(active|deprecated)$")


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
    versions: list[EvaVersionOut]
    created_at: datetime
