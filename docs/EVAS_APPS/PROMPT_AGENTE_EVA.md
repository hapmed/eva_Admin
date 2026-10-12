# PROMPT_AGENTE_EVA.md — Prompt para el agente que desarrollará la EVA

Pega el siguiente prompt al otro agente (OpenCode), sustituyendo lo que está
entre `[...]`.

---

## Prompt

Actúa como arquitecto y responsable técnico de HAPMED. Vas a construir una
**EVA** (aplicación de negocio) llamada **`[NOMBRE DE LA EVA]`** que hará:
**`[QUÉ HACE, EN 1–3 FRASES]`**.

Contexto obligatorio (léelo antes de programar):

- Carpeta de especificación del kit: `docs/EVAS_APPS/`
  - `COMO_FUNCIONA_EVAS_ADMIN.md` — cómo funciona la plataforma que la administrará.
  - `REQUISITOS_EVA.md` — el **contrato** que debes cumplir (obligatorio).
  - `DISENO_EVA.md` — el **diseño** a replicar (tokens y componentes).
  - `MANIFEST_EJEMPLO.yaml` — el manifiesto `eva.yaml`.
- Repositorio de referencia (público): <https://github.com/hapmed/eva_Admin>
  (panel EVAS Admin). **Reutiliza** de él:
  - `frontend/src/app.css` (tokens de marca) y `frontend/src/lib/components/*`.
  - Patrón de backend/FastAPI, Alembic, tests, Dockerfile y GitHub Actions.

### Requisitos que debes cumplir (resumen de `REQUISITOS_EVA.md`)

1. **Stack:** SvelteKit + TypeScript + Tailwind v4 (`@tailwindcss/vite`) +
   `@lucide/svelte` + `@sveltejs/adapter-node`; backend FastAPI + SQLAlchemy +
   Alembic + PostgreSQL (si aplica). Mismo diseño que EVAS Admin.
2. **Contenedores:** imagen Docker versionada (semver), no root, sin secretos,
   sin `privileged`, sin `docker.sock`.
3. **Contrato de contenedor:** escucha en `PORT`/`0.0.0.0`; `GET /healthz`
   devuelve 200 cuando está lista; logs saneados a stdout; apagado ordenado.
4. **Configuración:** declara `config_schema` (subconjunto JSON Schema) y recibe
   la configuración y secretos por **variables de entorno**
   (`EVAS_EVA_CODE`, `EVAS_INSTALLATION_ID`, `EVAS_CLIENT_REF`, `EVAS_VERSION`,
   `DATABASE_URL`, `PORT`, `DB_PASSWORD`…).
5. **Base de datos:** una **PostgreSQL por cliente**; migraciones idempotentes
   (`migrate`); datos respaldables/restaurables.
6. **Labels:** `evas.managed_by=evas-admin`, `evas.eva_code`, `evas.version`.
7. **Versiones:** semver; solo se desplegarán versiones `approved`; debe existir
   rollback. Expón la versión en `/healthz` o `/version`.
8. **Multi-tenant:** una instancia por cliente (por dominio); sin mezclar datos.
9. **Diseño:** replica tokens y componentes de `DISENO_EVA.md` (tema claro/oscuro,
   accesibilidad AA, estados de carga/vacío/error, responsive con barra lateral
   adaptable).

### Entregables

- Aplicación funcional (frontend + backend) con el diseño indicado.
- `eva.yaml` (manifiesto) según el ejemplo.
- `Dockerfile`(s) y `compose.yaml` de desarrollo (sin servicio PostgreSQL
  productivo).
- Migraciones Alembic y pruebas (unitarias/API) en verde.
- CI en GitHub Actions: lint/tipos/pruebas y **publicación de la imagen en GHCR**
  (`ghcr.io/hapmed/eva-<code>:<version>` y `sha-<commit>`).
- Documentación breve: cómo se configura, cómo se despliega, variables de
  entorno (valores ficticios en `.env.example`).

### Reglas de trabajo

- **Documenta antes de programar** y respeta `REQUISITOS_EVA.md`.
- **Sin secretos** en el repositorio ni en logs.
- No asumas infraestructura: usa variables de entorno y valores ficticios.
- Reporta **solo** pruebas que se hayan ejecutado, con resultados reales.

Empieza propuesta de arquitectura y estructura de carpetas; si algo de
`[NOMBRE DE LA EVA]` no está claro, pregunta antes de implementar.

---

### Notas para quien lanza el prompt (HAPMED)

- El nombre `code` de la EVA debe ser **estable** (no cambiarlo después).
- Una vez tengas la imagen publicada en GHCR, se **registra la EVA** en EVAS
  Admin (catálogo) con sus versiones `approved`, y a partir de ahí puede
  instalarse por cliente.
