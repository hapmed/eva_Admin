# Changelog

Formato basado en *Keep a Changelog*. Fechas en UTC.

## [Fase 7] - 2026-10-11
### Añadido
- Informe de auditoría final (`docs/EVAS_ADMIN/AUDIT_REPORT.md`).
- `CHANGELOG.md`.
### Verificado
- Contraste código ↔ documentación; suite completa ejecutada y reportada.

## [Fase 6] - 2026-10-11
### Añadido
- Rate limiting por IP/alcance en rutas sensibles.
- Manejador global de errores sin detalles internos.
- Robustez del agente: fallos registrados como operación `failed` (`agent_error`).
- Pruebas: `test_rate_limit`, `test_migrations`, `test_agent_failure`.
- Frontend: `vitest` con pruebas unitarias (`format.test.ts`).
- Rotación de logs en `ops/compose.yaml`.

## [Fase 5] - 2026-10-11
### Añadido
- Monitoreo: `HealthCheck`, `Metric`, endpoints de salud/logs/métricas saneados.
- Política de backup en actualizaciones (copia simulada por base).
- Alertas (`GET /alerts`, acknowledge/resolve).
- Migración `0003_monitoring`.

## [Fase 4] - 2026-10-11
### Añadido
- Infraestructura lógica: nodos, instalaciones, servicios, dominios, bases de datos, config, referencias a secretos, operaciones tipadas con idempotencia.
- Migración `0002_provisioning`.

## [Fase 3] - 2026-10-11
### Añadido
- Auth dual (cookie + CSRF y token Bearer).
- Usuarios internos, roles y permisos; clientes y usuarios de cliente.
- Catálogo EVA y versiones; planes y suscripciones con historial y vencimientos.
- Migración `0001_initial`.

## [Fase 2] - 2026-10-11
### Añadido
- Esqueleto backend (FastAPI), frontend (SvelteKit + Tailwind) y agente en modo `simulated`.
- Tokens de marca, tema claro/oscuro, navegación adaptable.

## [Fase 1] - 2026-10-11
### Añadido
- Decisiones de arquitectura (ADR): auth dual, BD por cliente, Cloudflare Tunnel, agente propio.

## [Fase 0] - 2026-10-11
### Añadido
- Especificación `docs/EVAS_ADMIN/` (12 documentos) y prompts por fase.
