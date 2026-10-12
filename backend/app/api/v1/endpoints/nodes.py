"""Nodos (hosts Docker)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.serializers import node_out
from app.db.session import get_db
from app.schemas.installation import NodeOut
from app.services import node_service

router = APIRouter()


@router.get("", response_model=list[NodeOut])
def list_nodes(
    _: AuthContext = Depends(require_permission("installations:read")),
    db: Session = Depends(get_db),
) -> list[dict]:
    return [node_out(node) for node in node_service.list_nodes(db)]
