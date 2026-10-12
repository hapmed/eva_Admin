"""Esquemas de usuarios internos de las apps EVA."""

from pydantic import BaseModel, Field


class EvaUserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: str | None


class EvaUserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=200)
    full_name: str = Field(default="", max_length=200)
    role: str = Field(default="user", max_length=60)


class EvaUserReset(BaseModel):
    password: str = Field(min_length=8, max_length=200)
