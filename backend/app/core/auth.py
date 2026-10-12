"""Contexto de autenticación (independiente de la capa HTTP)."""

from dataclasses import dataclass, field


@dataclass
class AuthContext:
    actor_type: str  # hapmed_user | integration
    actor_id: str
    method: str  # cookie | bearer
    permissions: set[str] = field(default_factory=set)
