# EVAS Admin

Monorepo del panel de administración de HAPMED. La **especificación** es la
fuente de verdad en [`docs/EVAS_ADMIN/`](docs/EVAS_ADMIN/).

## Estructura

| Carpeta | Contenido |
|---------|-----------|
| `backend/` | API FastAPI + SQLAlchemy + Alembic (Fase 2: esqueleto). |
| `frontend/` | SvelteKit 3 + TypeScript + Tailwind CSS v4 (Fase 2). |
| `agent/` | Agente de operaciones restringido (modo `simulated`). |
| `ops/` | `compose.yaml` (sin servicio PostgreSQL). |
| `docs/EVAS_ADMIN/` | Especificación funcional y técnica. |
| `prompts/EVAS_ADMIN/` | Prompts de especificación por fase. |
| `brand/` | Activos de marca HAPMED. |

## Desarrollo local

```bash
# Backend (http://localhost:8000/docs)
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend (http://localhost:5173)
cd frontend
npm install
npm run dev

# Agente (http://localhost:8001)
cd agent
uv sync
EVAS_AGENT_TOKEN=dev-token uv run uvicorn app.main:app --port 8001
```

Configuración: copiar [`.env.example`](.env.example) a `.env` (valores ficticios).

## Calidad

```bash
# backend y agent
uv run ruff check . && uv run mypy app && uv run pytest

# frontend
npm run check && npm run lint && npm run test && npm run build
```

## Estado del proyecto

- **Fase 0** — Documentación ✅
- **Fase 1** — Arquitectura y decisiones ✅
- **Fase 2** — Esqueleto (backend, frontend, agente en modo simulado) ✅
- **Fase 3** — Usuarios, clientes, EVA y suscripciones ✅
- **Fase 4** — Instalaciones, dominios, bases de datos y operaciones ✅
- **Fase 5** — Monitoreo, alertas y actualizaciones seguras ✅
- **Fase 6** — Seguridad, contenedores y pruebas ✅
- Fase 7 — Pendiente.

Sin conexión al PostgreSQL existente ni operaciones Docker reales.

## Seguridad

Ver [`docs/EVAS_ADMIN/SECURITY.md`](docs/EVAS_ADMIN/SECURITY.md). El archivo
local `contras.txt` está excluido de Git.
