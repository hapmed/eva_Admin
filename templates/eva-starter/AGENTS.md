# AGENTS.md — Guía para el agente (plantilla de EVA)

Este proyecto es una **EVA** de HAPMED, construida desde `templates/eva-starter`
y pensada para ser **administrada y desplegada por EVAS Admin**.

**Contrato obligatorio** (léelo antes de programar), en el repositorio de
referencia <https://github.com/hapmed/eva_Admin>:

- `docs/EVAS_APPS/REQUISITOS_EVA.md` — requisitos/contrato.
- `docs/EVAS_APPS/DISENO_EVA.md` — diseño a replicar.
- `docs/EVAS_APPS/MANIFEST_EJEMPLO.yaml` — manifiesto `eva.yaml`.

## Estructura

| Ruta | Contenido |
|------|-----------|
| `eva.yaml` | Manifiesto (contrato con EVAS Admin). |
| `backend/` | FastAPI + SQLAlchemy + Alembic (`app/`, `alembic/`, `tests/`). |
| `frontend/` | SvelteKit 3 + TypeScript + Tailwind v4 (`src/`). |
| `ops/compose.yaml` | Compose de desarrollo (sin PostgreSQL productivo). |

## Comandos de calidad (ejecutar antes de commit)

```bash
# Backend
cd backend
uv sync
uv run ruff check .
uv run mypy app
uv run pytest

# Frontend
cd frontend
npm install
npm run check      # svelte-check
npm run lint       # prettier --check
npm run test       # vitest
npm run build
```

## Desarrollo local

```bash
# Backend  → http://localhost:8000/docs
cd backend && uv sync && uv run uvicorn app.main:app --reload
# Frontend → http://localhost:5173
cd frontend && npm install && npm run dev
```

Configuración: copiar `.env.example` a `.env` (valores ficticios).

## Convenciones

- Documentación y UI en español; identificadores de código en inglés.
- Fechas en UTC.
- Reglas de negocio en `backend/app/services/`; endpoints finos.
- Diseño: usa los componentes de `frontend/src/lib/components/` y los tokens de
  `frontend/src/app.css` (no inventar estilos nuevos).

## Seguridad (obligatorio)

- **Nunca** versionar secretos; `.env` fuera de Git.
- Nunca registrar contraseñas, tokens ni cadenas de conexión.
- Configuración solo por variables de entorno; secretos por referencia.
- Sin `privileged`, sin `docker.sock`, proceso no root; imágenes con versión fija (no `latest`).
- No exponer datos entre clientes: **una base PostgreSQL por cliente**.

## Contrato de contenedor (recordatorio)

- Escucha en `PORT`/`0.0.0.0`; `GET /healthz` devuelve `200` cuando está lista.
- Configuración y secretos por variables de entorno
  (`EVAS_VERSION`, `EVAS_EVA_CODE`, `EVAS_INSTALLATION_ID`, `EVAS_CLIENT_REF`,
  `DATABASE_URL`, `PORT`, `DB_PASSWORD`…).
- Labels: `evas.managed_by=evas-admin`, `evas.eva_code`, `evas.version`.
- Versión semver; solo se desplegarán versiones `approved`. Expón tu versión en `/healthz`.

## Publicación

`publish.yml` publica en GHCR al hacer push a `main`:
`ghcr.io/<owner>/<repo>-{api,web}` (tags `latest` y `sha-<commit>`). Tras publicar,
se registra la EVA en EVAS Admin con sus versiones `approved`.
