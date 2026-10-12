"""Esquemas de clientes y usuarios de cliente."""

from datetime import datetime

from pydantic import BaseModel, Field


class ClientCreate(BaseModel):
    legal_name: str = Field(min_length=1, max_length=200)
    display_name: str = Field(min_length=1, max_length=200)
    tax_id: str | None = Field(default=None, max_length=60)
    notes: str = Field(default="", max_length=500)


class ClientUpdate(BaseModel):
    legal_name: str | None = Field(default=None, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)
    tax_id: str | None = Field(default=None, max_length=60)
    notes: str | None = Field(default=None, max_length=500)


class ClientOut(BaseModel):
    id: str
    legal_name: str
    display_name: str
    tax_id: str | None
    status: str
    notes: str
    created_at: datetime


class ClientUserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=200)
    role_code: str = Field(default="client_viewer", max_length=64)


class ClientUserUpdate(BaseModel):
    role_code: str | None = Field(default=None, max_length=64)
    is_active: bool | None = None


class ClientUserOut(BaseModel):
    id: str
    client_id: str
    email: str
    role_code: str
    is_active: bool
    created_at: datetime
