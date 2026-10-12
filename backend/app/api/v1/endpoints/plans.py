"""Planes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.errors import http_error
from app.api.serializers import plan_out
from app.db.session import get_db
from app.schemas.subscription import PlanCreate, PlanOut
from app.services import subscription_service

router = APIRouter()


@router.get("", response_model=list[PlanOut])
def list_plans(
    _: AuthContext = Depends(require_permission("plans:read")), db: Session = Depends(get_db)
) -> list[dict]:
    return [plan_out(plan) for plan in subscription_service.list_plans(db)]


@router.post("", response_model=PlanOut, status_code=201)
def create_plan(
    data: PlanCreate,
    context: AuthContext = Depends(require_permission("plans:manage")),
    db: Session = Depends(get_db),
) -> dict:
    try:
        plan = subscription_service.create_plan(db, context, data)
    except (ValueError, LookupError) as exc:
        raise http_error(exc) from exc
    return plan_out(plan)
