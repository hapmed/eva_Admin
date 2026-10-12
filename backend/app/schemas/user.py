"""Esquemas de usuarios, roles y permisos."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    full_name: str = Field(default="", max_length=200)
    password: str = Field(min_length=8, max_length=200)
    roles: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None


class UserRolesUpdate(BaseModel):
    roles: list[str] = Field(default_factory=list)


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    mfa_enabled: bool
    roles: list[str]
    created_at: datetime


class PermissionOut(BaseModel):
    code: str
    description: str


class RoleOut(BaseModel):
    id: str
    code: str
    name: str
    is_system: bool
    permissions: list[str]


class RolePermissionsUpdate(BaseModel):
    permissions: list[str] = Field(default_factory=list)
