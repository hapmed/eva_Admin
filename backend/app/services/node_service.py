"""Nodos (hosts Docker donde corren las instalaciones)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.infrastructure import Node


def list_nodes(db: Session) -> list[Node]:
    return list(db.scalars(select(Node).order_by(Node.name)).all())
