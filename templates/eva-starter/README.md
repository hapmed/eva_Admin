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

## Branding por cliente

Este repositorio (`hapmed/eva`) es **uno solo** que se **modifica/rebrandea por
cliente**. Para personalizar la apariencia:

1. Reemplaza los activos en `frontend/static/brand/`:
   - `logo-mark.png` (símbolo), `logo-appicon.png`, `favicon-64.png`,
     `apple-touch-icon.png`, `og-image.png`.
2. Ajusta el nombre visible (por defecto «HAPMED») donde se muestra
   (`frontend/src/routes/+layout.svelte` y `frontend/src/routes/login/+page.svelte`
   si aplica) o usa la variable `EVA_CLIENT_NAME`.
3. Opcional: el color de acento y demás tokens están en `frontend/src/app.css`
   (`--color-accent`, `--color-accent-2`); cámbialos si el cliente tiene paleta.

> Mantén `eva.yaml` con `code`/`image` estables; el branding no cambia el
> contrato con EVAS Admin.

## Credenciales

El archivo `contras.txt` (credenciales del VPS/PostgreSQL/Cloudflare) se incluye
en esta carpeta **solo para el desarrollo** y **NO se versiona** (está en
`.gitignore`). Nunca lo subas a Git ni lo compartas.

