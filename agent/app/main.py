"""Servicio HTTP mínimo del agente de operaciones (esqueleto Fase 2)."""

import logging

from fastapi import Depends, FastAPI, HTTPException, status

from app.audit import record
from app.auth import require_token
from app.config import get_settings
from app.operations import OperationRequest, OperationResult, execute

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="EVAS Admin Agent",
    version="0.1.0",
    description="Agente restringido de operaciones (modo simulado por defecto).",
)


@app.get("/healthz", summary="Liveness")
def healthz() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "mode": settings.agent_mode}


@app.post(
    "/v1/operations",
    response_model=OperationResult,
    dependencies=[Depends(require_token)],
    summary="Ejecutar una operación tipada",
)
def run_operation(request: OperationRequest) -> OperationResult:
    try:
        result = execute(request, get_settings().agent_mode)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc
    except RuntimeError as exc:  # modo real no habilitado
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(exc)
        ) from exc

    record(request.type.value, request.installation_id, result.status, simulated=result.simulated)
    return result
