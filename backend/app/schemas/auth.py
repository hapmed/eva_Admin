"""Esquemas de autenticación, sesión y passkeys."""

from datetime import datetime

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
    passkey_name: str | None = None
    has_passkeys: bool = False


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)


class WebAuthnRegisterComplete(BaseModel):
    credential: dict
    name: str | None = Field(default=None, max_length=80)


class WebAuthnLoginBegin(BaseModel):
    email: str | None = Field(default=None, max_length=320)


class WebAuthnLoginComplete(BaseModel):
    credential: dict


class CredentialOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    last_used_at: datetime | None
