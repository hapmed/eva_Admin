# EVAS Admin — Backend (FastAPI)

Esqueleto de la API (Fase 2). **No** ejecuta operaciones Docker reales ni se
conecta al PostgreSQL existente.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Ejecución local

```bash
uv sync                 # instala dependencias
uv run uvicorn app.main:app --reload
```

- Documentación OpenAPI: <http://localhost:8000/docs>
- Salud: `GET /healthz` · Readiness: `GET /readyz`

## Calidad

```bash
uv run ruff check .
uv run pytest
```

## Configuración

Todas las variables usan el prefijo `EVAS_` (ver `.env.example` en la raíz del
repositorio). Los valores por defecto son ficticios.

## Base de datos

- Fase 2 **no** abre conexiones. El engine se crea de forma perezosa.
- El driver `psycopg` se instala con el extra `postgres` cuando se conecte a la
  base administrativa real (Fase 3/4):
  `uv sync --extra postgres`.
- Migraciones con Alembic (`alembic/`). **No** ejecutar contra el PostgreSQL
  existente sin autorización (ver `docs/EVAS_ADMIN/POSTGRES_EXISTING_INSTANCE.md`).
