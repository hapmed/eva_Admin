# AGENTS.md — Guía de agentes y desarrollo (EVAS Admin)

Repositorio: <https://github.com/hapmed/eva_Admin> · Especificación: [`docs/EVAS_ADMIN/`](docs/EVAS_ADMIN/).
Estado: fases 0-7 completadas. El agente opera en modo `simulated`; **no** se toca
el PostgreSQL existente ni Docker real sin autorización.

## Estructura

| Ruta | Contenido |
|------|-----------|
| `backend/` | API FastAPI + SQLAlchemy + Alembic (`app/`, `alembic/`, `tests/`). |
| `agent/` | Agente de operaciones restringido (modo `simulated`). |
| `frontend/` | SvelteKit 3 + TypeScript + Tailwind v4 (`src/`). |
| `ops/` | `compose.yaml` (sin servicio PostgreSQL). |
| `brand/` | Activos de marca. |
| `docs/EVAS_ADMIN/` | Especificación + `AUDIT_REPORT.md`. |
| `prompts/EVAS_ADMIN/` | Prompts por fase. |

## Comandos de calidad (ejecutar antes de commit)

```bash
# Backend
cd backend
uv sync
uv run ruff check .        # lint
uv run ruff format --check .
uv run mypy app            # tipos
uv run pytest              # pruebas

# Agente
cd agent
uv sync
uv run ruff check . && uv run mypy app && uv run pytest

# Frontend
cd frontend
npm install
npm run check              # svelte-check (tipos)
npm run lint               # prettier --check
npm run test               # vitest
npm run build
```

Valores de referencia actuales: backend `pytest` 52/52; frontend `vitest` 4/4.

## Desarrollo local

```bash
# Backend  → http://localhost:8000/docs
cd backend && uv sync && uv run uvicorn app.main:app --reload
# Frontend → http://localhost:5173
cd frontend && npm install && npm run dev
# Agente   → http://localhost:8001
cd agent && uv sync && EVAS_AGENT_TOKEN=dev-token uv run uvicorn app.main:app --port 8001
```

Configuración: copiar [`.env.example`](.env.example) a `.env` (valores ficticios).
Primer administrador: `ensure_superadmin(...)` en `backend/app/db/bootstrap.py`.

## Convenciones

- Documentación y UI en español; identificadores de código en inglés.
- Fechas en UTC; mostrar en zona configurada.
- Reglas de negocio en `backend/app/services/`; endpoints finos.
- Migraciones **nunca** contra el PostgreSQL existente sin autorización.
- Marcar datos no confirmados como `[POR VERIFICAR]`, `[PROPUESTA]`, `[CONFIRMADO]`.

## Seguridad (obligatorio)

- **Nunca** versionar secretos; `.env` fuera de Git; `contras.txt` ignorado.
- Nunca registrar contraseñas, tokens, cookies ni cadenas de conexión.
- No montar `/var/run/docker.sock` salvo en el contenedor del agente y en modo `real`.
- No `privileged`; imágenes con versión fija (no `latest`); procesos no root.
- Operaciones destructivas (restore, downgrade) requieren confirmación y auditoría.

## Runbook de despliegue en VPS

Prerrequisitos (fuera del repositorio): Docker + Compose, Cloudflare Tunnel
(opcional), base administrativa **ya creada y autorizada** en la instancia
PostgreSQL existente, y `.env` real en el servidor.

```bash
git clone https://github.com/hapmed/eva_Admin && cd eva_Admin
cp .env.example .env      # editar con valores reales (no versionar)
```

### 1. Migraciones (base administrativa)

```bash
# Opción A: con uv en el host
cd backend && uv sync && uv run alembic upgrade head && uv run alembic current

# Opción B: con la imagen (tras el primer build)
docker compose -f ops/compose.yaml run --rm api alembic upgrade head
```

### 2. Sembrar permisos/roles y administrador

```bash
docker compose -f ops/compose.yaml run --rm api python -c \
"from app.db.seed import seed; from app.db.session import get_session_factory; seed(get_session_factory()())"
# Crear el primer admin (idempotente) con credenciales reales:
docker compose -f ops/compose.yaml run --rm api python -c \
"from app.db.bootstrap import ensure_superadmin; from app.db.session import get_session_factory; ensure_superadmin(get_session_factory()(), 'admin@hapmed.example', 'CAMBIA-ESTO')"
```

### 3. Desplegar imágenes (GHCR)

Las imágenes se publican automáticamente en GHCR (`publish.yml`) como
`ghcr.io/hapmed/evas-admin-{api,web,agent}:latest` y `:sha-<commit>`. Los
paquetes son **públicos** (no requieren `docker login`).

```bash
docker compose -f ops/compose.prod.yaml pull
docker compose -f ops/compose.prod.yaml up -d
docker compose -f ops/compose.prod.yaml ps
```

### 4. Verificación

```bash
docker compose -f ops/compose.yaml exec api python -c \
"import urllib.request; print(urllib.request.urlopen('http://localhost:8000/healthz').read())"
# Web en el puerto interno 3000 (publicar vía Cloudflare Tunnel/proxy).
```

### 5. Actualización y rollback

```bash
# Actualizar a la última publicada
git pull
docker compose -f ops/compose.prod.yaml pull
docker compose -f ops/compose.prod.yaml run --rm api alembic upgrade head
docker compose -f ops/compose.prod.yaml up -d

# Rollback a un commit concreto (imagen etiquetada sha-<commit>)
echo 'EVAS_IMAGE_TAG=sha-<commit>' >> .env
docker compose -f ops/compose.prod.yaml pull && docker compose -f ops/compose.prod.yaml up -d
# (elimina EVAS_IMAGE_TAG del .env para volver a :latest)

# Downgrade de esquema (SÓLO con autorización y respaldo previo):
docker compose -f ops/compose.prod.yaml run --rm api alembic downgrade -1
```

## Integración continua (GitHub Actions)

- `.github/workflows/ci.yml` — backend (ruff, mypy, pytest), agente y frontend
  (check, lint, test, build) en cada push/PR.
- `.github/workflows/publish.yml` — en push a `main` construye y publica las tres
  imágenes en GHCR (`latest` y `sha-<commit>`). Build local opcional con
  `docker compose -f ops/compose.prod.yaml build`.

## Requiere autorización humana

- Ejecutar migraciones en el PostgreSQL existente.
- Crear base/rol administrativos en la instancia existente.
- Habilitar el agente en modo `real` (Docker) y montar el socket.
- Publicar (Cloudflare Tunnel) y ejecutar operaciones destructivas.
