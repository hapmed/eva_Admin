# EVAS Admin — Agente de operaciones

Servicio restringido que ejecuta operaciones **tipadas** sobre Docker. En Fase 2
sólo funciona en modo `simulated` y **no** monta el socket Docker (ADR-007).

## Ejecución local

```bash
uv sync
EVAS_AGENT_TOKEN=dev-token uv run uvicorn app.main:app --port 8001
```

- Salud: `GET /healthz`
- Operación: `POST /v1/operations` (requiere `Authorization: Bearer <token>`)

## Modos

- `simulated` (por defecto): no realiza cambios reales.
- `real`: **deshabilitado** en Fase 2; requiere autorización y revisión de
  seguridad (ver `docs/EVAS_ADMIN/SECURITY.md`).

## Calidad

```bash
uv run ruff check .
uv run pytest
```
