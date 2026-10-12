"""Esquemas de autenticación y sesión."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=200)


class CsrfResponse(BaseModel):
    csrf_token: str


class MeResponse(BaseModel):
    id: str
    email: str
    full_name: str
    roles: list[str]
    permissions: list[str]
