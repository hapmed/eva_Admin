# IMPLEMENTATION_PLAN.md — Plan de implementación de EVAS Admin

**Estado:** Borrador inicial.
**Documentos relacionados:** todos los de `docs/EVAS_ADMIN/`.
**Regla transversal:** documentación antes que código; cada fase se aprueba antes
de la siguiente.

## 1. Resumen de fases

| Fase | Nombre | Prompt | Estado |
|------|--------|--------|--------|
| 0 | Documentación de especificación | `00_*` | **Completada (este entregable)** |
| 1 | Arquitectura y plan detallado | `01_*` | **Completada** |
| 2 | Diseño responsive y estructura base | `02_*` | **Completada** |
| 3 | Usuarios, clientes, productos y suscripciones | `03_*` | **Completada** |
| 4 | Instalaciones, dominios y bases de datos | `04_*` | **Completada** |
| 5 | Monitoreo Docker y actualizaciones | `05_*` | **Completada** |
| 6 | Seguridad, contenedores y pruebas | `06_*` | Pendiente |
| 7 | Auditoría final y entrega | `07_*` | Pendiente |

## 2. Fase 0 — Documentación (completada)

**Entregable:** esta carpeta `docs/EVAS_ADMIN/`.

**Criterios de aceptación:**
- [x] Existen los 12 documentos de especificación.
- [x] Coherencia entre documentos (mismas entidades, roles y decisiones).
- [x] Sin secretos ni datos reales sensibles.
- [x] Decisiones marcadas como CONFIRMADO/PROPUESTA/POR VERIFICAR.
- [x] PostgreSQL existente tratado como preexistente.

## 3. Fase 1 — Arquitectura y plan detallado (completada)

**Objetivo:** cerrar decisiones abiertas y afinar modelo/endpoints/plan.

**Decisiones cerradas:**
- ADR-009 auth: **dual** (cookie SPA + token integraciones/agente).
- ADR-012 aislamiento: **una base de datos por cliente**.
- ADR-010 túnel: **Cloudflare Tunnel**.
- ADR-007 agente: **se construye en este proyecto**.
- Añadidos ADR-015 (pruebas) y ADR-016 (observabilidad/recuperación).

**Criterios de aceptación:**
- [x] `ARCHITECTURE.md`, `DATA_MODEL.md`, `API_CONTRACTS.md`, `SECURITY.md`,
  `IMPLEMENTATION_PLAN.md` y `DECISIONS.md` actualizados.
- [x] Sin contradicciones entre documentos.
- [x] Riesgos y plan ejecutable documentados.
- [x] Diagramas de instalación y actualización definidos.

**Pendiente de insumo:** instancia PostgreSQL existente
([`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md)).

## 4. Fase 2 — Diseño y estructura base (completada)

**Objetivo:** esqueleto de frontend y backend que arranca sin tocar
infraestructura real.

**Frontend:** SvelteKit 3 + TS + Tailwind v4, tokens de marca (Apple HIG),
componentes base, navegación adaptable (barra lateral/pestañas), estados de UI,
accesibilidad y tema claro/oscuro.
**Backend:** FastAPI modular, config por entorno, esquema SQLAlchemy y Alembic
configurado (sin migrar a prod), `/healthz` y `/readyz`, OpenAPI, `.env.example`.
**Agente:** servicio `agent/` en modo `simulated`, contrato de operaciones
tipadas y autenticación por token — sin tocar Docker real.

**Criterios de aceptación:**
- [x] Proyecto (web, api, agente simulado) construye/arranca en local.
- [x] Lint, typecheck y pruebas en verde (resultados reales abajo).
- [x] **No** se conecta a Docker real ni se modifica PostgreSQL existente.
- [x] README actualizado.

**Resultados verificados (Fase 2):**
- Backend: `ruff` limpio, `mypy` limpio, `pytest` 14/14.
- Agente: `ruff` limpio, `mypy` limpio, `pytest` 11/11.
- Frontend: `svelte-check` 0 errores, `prettier --check` OK, `vite build` OK.

## 5. Fase 3 — Usuarios, clientes, productos y suscripciones (completada)

**Objetivo:** módulos de identidad y comercial.

**Tareas:** usuarios internos + roles/permisos; clientes y usuarios de cliente;
catálogo EVA y versiones; planes y suscripciones con historial y alertas de
vencimiento. Autenticación dual (cookie + CSRF / token), auditoría y aislamiento
por cliente.

**Criterios de aceptación:**
- [x] CRUD lógico funcional con auditoría.
- [x] Aislamiento multi-tenant probado (usuarios de cliente por cliente).
- [x] Sin autoelevación de privilegios (roles propios y estado propio bloqueados).
- [x] Fechas en UTC (cálculo de vencimientos por periodo).
- [ ] Migración aplicada a un PostgreSQL local — **pendiente de autorización**.

**Resultados verificados (Fase 3):**
- Backend: `ruff` limpio, `mypy` limpio, `pytest` **36/36**.
- Migración `0001_initial` validada en modo offline (`alembic upgrade --sql`).
  Las pruebas usan SQLite en memoria; **no** se tocó el PostgreSQL existente.
- Frontend: `svelte-check` 0 errores, `prettier --check` OK, `vite build` OK.

## 6. Fase 4 — Instalaciones, dominios y bases de datos (completada)

**Objetivo:** gestión lógica de instalaciones (sin aprovisionamiento real).

**Tareas:** entidades separadas (cliente, suscripción, EVA, instalación,
servicio, dominio, base de datos, config, referencia a secretos); **registro de
la base de negocio por cliente** (ADR-012) sin exponer credenciales; detección de
conflicto de dominio; contrato del agente + integración con el servicio.

**Criterios de aceptación:**
- [x] Pruebas de aislamiento, conflicto de dominio, idempotencia y errores.
- [x] El agente en modo `simulated` indica claramente que **no** hubo cambios reales.
- [x] Sin exponer credenciales (sólo metadatos y referencias a secretos).
- [x] Configuración validada contra el esquema permitido de cada EVA.

**Resultados verificados (Fase 4):**
- Backend: `ruff` limpio, `mypy` limpio, `pytest` **44/44**.
- Migración `0002_provisioning` validada en modo offline; cadena `0001 -> 0002`.
- Frontend: `svelte-check` 0 errores, `prettier --check` OK, `vite build` OK.

## 7. Fase 5 — Monitoreo Docker y actualizaciones (completada)

**Objetivo:** monitoreo y actualizaciones con el agente en modo `simulated`.

**Tareas:** estado/healthcheck/versiones/métricas; historial de eventos y logs
saneados; operaciones por rol (restart, upgrade, health-check, backup/restore);
flujo de actualización con validación, backup, healthchecks y auditoría;
alertas configurables.

**Criterios de aceptación:**
- [x] Pruebas de permisos, fallos e idempotencia.
- [x] `/var/run/docker.sock` no expuesto a FE/API.
- [x] Sin shell arbitrario ni parámetros arbitrarios.
- [x] Logs/métricas saneados y en modo simulado (nunca se inventan datos).

**Resultados verificados (Fase 5):**
- Backend: `ruff` limpio, `mypy` limpio, `pytest` **49/49**.
- Migración `0003_monitoring` validada en modo offline (`0001 -> 0002 -> 0003`).
- Frontend: `svelte-check` 0 errores, `prettier --check` OK, `vite build` OK.

## 8. Fase 6 — Seguridad, contenedores y pruebas

**Objetivo:** endurecer y empaquetar.

**Tareas:** auth/authz; CSRF si aplica; CORS; rate limiting; validación; gestión
de secretos; auditoría; versiones fijas; no-root; healthchecks; rotación de logs;
`Dockerfile` backend y frontend; `compose.yaml`; `.dockerignore`, `.gitignore`,
`.env.example`; documentación de backup/restore/update/rollback.

**Criterios de aceptación:**
- Suite de pruebas (unitarias, API, roles, aislamiento, fechas, migraciones en
  base de prueba, fallos del agente).
- Sin secretos en Git/logs.
- **No** se modifica ni reinicia el PostgreSQL existente.

## 9. Fase 7 — Auditoría final y entrega

**Objetivo:** verificar coherencia código↔documentación y entregar.

**Criterios de aceptación:**
- Checklist de [`07_PROMPT_AUDITORIA_FINAL.md`](../../prompts/EVAS_ADMIN/07_PROMPT_AUDITORIA_FINAL.md)
  verificado.
- Sin afirmaciones de pruebas/despliegues que no ocurrieron.
- `CHANGELOG.md` y este plan actualizados.

## 10. Riesgos y dependencias globales

| Riesgo | Impacto | Mitigación |
|--------|---------|-----------|
| Datos insuficientes de la instancia PG | Bloquea conexión | Inspección segura + confirmación ([doc](./POSTGRES_EXISTING_INSTANCE.md)) |
| Agente real requiere revisión de seguridad | Riesgo de exposición Docker | Modo `simulated` por defecto; modo `real` tras autorización |
| Decisiones ADR abiertas | Retrabajo | Resolver en Fase 1 |
| Aislamiento multi-tenant | Seguridad | Pruebas obligatorias + revisión |
| Exposición de secretos | Crítico | Revisión + tooling + `.env` fuera de Git |

## 11. Definición de "terminado" (DoD) por fase

1. Código y documentación coherentes.
2. Lint, typecheck y pruebas ejecutados con resultados reportados.
3. Sin secretos versionados.
4. Sin cambios sobre infraestructura preexistente sin autorización.
5. Aprobación humana de la fase.
