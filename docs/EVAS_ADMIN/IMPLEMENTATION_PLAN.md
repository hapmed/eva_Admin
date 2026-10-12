# IMPLEMENTATION_PLAN.md — Plan de implementación de EVAS Admin

**Estado:** Borrador inicial.
**Documentos relacionados:** todos los de `docs/EVAS_ADMIN/`.
**Regla transversal:** documentación antes que código; cada fase se aprueba antes
de la siguiente.

## 1. Resumen de fases

| Fase | Nombre | Prompt | Estado |
|------|--------|--------|--------|
| 0 | Documentación de especificación | `00_*` | **Completada (este entregable)** |
| 1 | Arquitectura y plan detallado | `01_*` | Pendiente |
| 2 | Diseño responsive y estructura base | `02_*` | Pendiente |
| 3 | Usuarios, clientes, productos y suscripciones | `03_*` | Pendiente |
| 4 | Instalaciones, dominios y bases de datos | `04_*` | Pendiente |
| 5 | Monitoreo Docker y actualizaciones | `05_*` | Pendiente |
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

## 3. Fase 1 — Arquitectura y plan detallado

**Objetivo:** cerrar decisiones abiertas y afinar modelo/endpoints/plan.

**Tareas:**
- Resolver ADR-009 (auth), ADR-012 (aislamiento de datos), ADR-010 (túnel).
- Confirmar existencia del agente de operaciones (ADR-007).
- Afinar diagramas de instalación/actualización.

**Criterios de aceptación:**
- `ARCHITECTURE.md`, `DATA_MODEL.md`, `API_CONTRACTS.md`, `SECURITY.md`,
  `IMPLEMENTATION_PLAN.md` y `DECISIONS.md` actualizados.
- Sin contradicciones entre documentos.
- Riesgos y plan ejecutable documentados.

**Dependencias:** confirmación de la instancia PostgreSQL
([`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md)).

## 4. Fase 2 — Diseño y estructura base

**Objetivo:** esqueleto de frontend y backend que arranca sin tocar
infraestructura real.

**Frontend:** SvelteKit+TS, Tailwind, componentes base, navegación
desktop/móvil, estados de UI, accesibilidad.
**Backend:** FastAPI modular, config por entorno, esquema SQLAlchemy y Alembic
configurado (sin migrar a prod), `/healthz` y `/readyz`, OpenAPI, `.env.example`.

**Criterios de aceptación:**
- Proyecto arranca en local.
- Lint, typecheck y pruebas en verde (reportar resultados reales).
- **No** se conecta a Docker real ni se modifica PostgreSQL existente.
- README actualizado.

## 5. Fase 3 — Usuarios, clientes, productos y suscripciones

**Objetivo:** módulos de identidad y comercial.

**Tareas:** usuarios internos + roles/permisos; clientes y usuarios de cliente;
catálogo EVA y versiones; planes y suscripciones con historial y alertas de
vencimiento.

**Criterios de aceptación:**
- CRUD lógico funcional con auditoría.
- Aislamiento multi-tenant probado.
- Sin autoelevación de privilegios.
- Fechas UTC y conversión en UI.
- Migraciones probadas en **base local**, no en la existente.

## 6. Fase 4 — Instalaciones, dominios y bases de datos

**Objetivo:** gestión lógica de instalaciones (sin aprovisionamiento real).

**Tareas:** entidades separadas (cliente, suscripción, EVA, instalación,
servicio, dominio, base de datos, config, referencia a secretos); detección de
conflicto de dominio; metadatos de BD sin credenciales; contrato del agente +
adaptador simulado.

**Criterios de aceptación:**
- Pruebas de aislamiento, conflicto de dominio, idempotencia y errores.
- El adaptador simulado indica claramente que **no** hubo cambios reales.
- Sin exponer credenciales.

## 7. Fase 5 — Monitoreo Docker y actualizaciones

**Objetivo:** monitoreo y actualizaciones con adaptador simulado.

**Tareas:** estado/healthcheck/versiones/métricas; historial de eventos y logs
saneados; operaciones por rol (restart, upgrade, health-check, backup/restore);
flujo de actualización con validación, backup, healthchecks y auditoría.

**Criterios de aceptación:**
- Pruebas de permisos, timeout, fallos, reintentos e idempotencia.
- `/var/run/docker.sock` no expuesto a FE/API.
- Sin shell arbitrario ni parámetros arbitrarios.

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
| Agente de operaciones inexistente | Bloquea ops reales | Adaptador simulado en MVP |
| Decisiones ADR abiertas | Retrabajo | Resolver en Fase 1 |
| Aislamiento multi-tenant | Seguridad | Pruebas obligatorias + revisión |
| Exposición de secretos | Crítico | Revisión + tooling + `.env` fuera de Git |

## 11. Definición de "terminado" (DoD) por fase

1. Código y documentación coherentes.
2. Lint, typecheck y pruebas ejecutados con resultados reportados.
3. Sin secretos versionados.
4. Sin cambios sobre infraestructura preexistente sin autorización.
5. Aprobación humana de la fase.
