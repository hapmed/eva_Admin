# eva-starter — Plantilla base de una EVA

Proyecto base para construir una **EVA** de HAPMED con el **mismo diseño** que
EVAS Admin y lista para ser administrada/desplegada por la plataforma.

Lee primero (fuera de esta carpeta): [`../../docs/EVAS_APPS/`](../../docs/EVAS_APPS/)
— `REQUISITOS_EVA.md`, `DISENO_EVA.md`, `MANIFEST_EJEMPLO.yaml`.

## Estructura

```
eva-starter/
├─ eva.yaml              # manifiesto (contrato con EVAS Admin)
├─ .env.example          # variables de entorno (ficticias)
├─ backend/              # FastAPI + SQLAlchemy + Alembic
│  └─ app/{main.py, api/health.py, core/config.py, db/…}
├─ frontend/             # SvelteKit 3 + TypeScript + Tailwind v4
│  └─ src/{app.css, lib/components/*, lib/nav.ts, routes/…}
├─ ops/compose.yaml      # desarrollo (sin PostgreSQL productivo)
└─ .github/workflows/    # CI + publicación en GHCR
```

## Puesta en marcha (local)

```bash
# Backend → http://localhost:8000/docs
cd backend && uv sync && uv run uvicorn app.main:app --reload

# Frontend → http://localhost:5173
cd frontend && npm install && npm run dev
```

## Personalizar

1. `eva.yaml`: cambia `code` (estable), `name`, `image` y `versions`.
2. `frontend/src/lib/nav.ts`: define tus módulos.
3. `frontend/src/routes/`: añade tus páginas (usa `PageHeader`, `DataTable`,
   `EmptyState`, `Modal`, `Button`, `StatusBadge` de `lib/components/`).
4. `backend/app/models/` + `backend/app/api/`: añade modelos y endpoints.
5. `backend/alembic/versions/`: crea tus migraciones (`uv run alembic revision --autogenerate -m "..."`).
6. Configuración: declara en `eva.yaml` → `config_schema` las claves permitidas.

## Calidad

```bash
cd backend && uv run ruff check . && uv run mypy app && uv run pytest
cd frontend && npm run check && npm run lint && npm run test && npm run build
```

## Conexión con EVAS Admin (resumen)

- Publica la imagen en GHCR (lo hace `publish.yml`): `ghcr.io/<owner>/<repo>-{api,web}`.
- Registra la EVA en EVAS Admin con sus versiones `approved`.
- La plataforma inyecta `EVAS_VERSION`, `EVAS_EVA_CODE`, `EVAS_INSTALLATION_ID`,
  `EVAS_CLIENT_REF`, `DATABASE_URL` (una base PostgreSQL por cliente).
- Cada despliegue se confirma con `GET /healthz` (debe responder `200`).

Ver el contrato completo en [`../../docs/EVAS_APPS/REQUISITOS_EVA.md`](../../docs/EVAS_APPS/REQUISITOS_EVA.md).
