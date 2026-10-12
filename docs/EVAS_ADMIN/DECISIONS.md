# DECISIONS.md — Registro de decisiones de arquitectura (ADR)

Formato: `ID · Estado · Decisión · Contexto · Consecuencias`.
Estados: **CONFIRMADO**, **PROPUESTA**, **POR VERIFICAR**, **RECHAZADO**.

---

## ADR-001 · Backend en Python + FastAPI
- **Estado:** CONFIRMADO
- **Contexto:** Se requiere API tipada, rápida y con documentación OpenAPI.
- **Decisión:** Python + FastAPI.
- **Consecuencias:** Ecosistema Pydantic/SQLAlchemy; documentación automática.

## ADR-002 · Frontend en SvelteKit + TypeScript
- **Estado:** CONFIRMADO
- **Contexto:** UI responsive mantenible, con componentes propios.
- **Decisión:** SvelteKit + TypeScript + Tailwind CSS.
- **Consecuencias:** Un solo lenguaje (TS) en frontend; SSR opcional.

## ADR-003 · SQLAlchemy + Alembic como ORM y migraciones
- **Estado:** CONFIRMADO
- **Contexto:** Se necesita ORM maduro y control de esquema versionado.
- **Decisión:** SQLAlchemy 2.x + Alembic.
- **Consecuencias:** Migraciones versionadas; no se ejecutan en prod sin
  autorización.

## ADR-004 · PostgreSQL preexistente como base administrativa
- **Estado:** CONFIRMADO
- **Contexto:** Ya existe un contenedor Docker con PostgreSQL.
- **Decisión:** Usar la instancia existente para la base administrativa; **no**
  crear otro contenedor ni alterar el existente.
- **Consecuencias:** Requiere inspección y confirmación previa
  ([`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md)).

## ADR-005 · Base administrativa separada de bases de negocio de clientes
- **Estado:** CONFIRMADO
- **Contexto:** Evitar mezcla de datos y acoplamiento.
- **Decisión:** La base administrativa de EVAS Admin es independiente de las
  bases de negocio de cada cliente.
- **Consecuencias:** Distintas conexiones, roles y respaldos.

## ADR-006 · Monolito modular en lugar de microservicios
- **Estado:** CONFIRMADO
- **Contexto:** Equipo pequeño; MVP rápido.
- **Decisión:** Un backend modular con límites internos claros.
- **Consecuencias:** Menos complejidad operativa; se puede extraer el agente.

## ADR-007 · Agente de operaciones separado y restringido
- **Estado:** CONFIRMADO (diseño) / POR VERIFICAR (implementación real)
- **Contexto:** No exponer el socket Docker a la API ni al frontend.
- **Decisión:** Operaciones Docker sólo mediante un servicio con operaciones
  **tipadas** y permisos mínimos.
- **Consecuencias:** En MVP se usa un **adaptador simulado**; el agente real
  requiere autorización humana.

## ADR-008 · Operation de Docker vía operaciones tipadas, sin shell
- **Estado:** CONFIRMADO
- **Contexto:** Riesgo de ejecución arbitraria desde HTTP.
- **Decisión:** Prohibido el shell arbitrario; sólo operaciones enumeradas.
- **Consecuencias:** Mayor seguridad; menos flexibilidad.

## ADR-009 · Autenticación: cookie HttpOnly + CSRF vs token
- **Estado:** POR VERIFICAR
- **Contexto:** Se necesita proteger sesión en SPA.
- **Opciones:** (a) cookie HttpOnly/Secure/SameSite + CSRF; (b) token Bearer.
- **Decisión:** Pendiente de confirmación.
- **Consecuencias:** Impacta CORS, almacenamiento y CSRF ([`SECURITY.md`](./SECURITY.md)).

## ADR-010 · Publicación mediante Cloudflare Tunnel
- **Estado:** PROPUESTA
- **Contexto:** Exponer el panel sin abrir puertos; etapas iniciales.
- **Decisión propuesta:** Preparar compatibilidad con Cloudflare Tunnel; no
  exigir configuración productiva en esta etapa.
- **Consecuencias:** HTTPS gestionado; requiere definir DNS y políticas.

## ADR-011 · PWA como mejora opcional, no bloqueante
- **Estado:** CONFIRMADO
- **Contexto:** Podría aportar valor móvil, pero no debe retrasar el MVP.
- **Decisión:** Evaluar PWA tras el MVP.
- **Consecuencias:** Sin manifest/service worker en el MVP.

## ADR-012 · Estrategia de aislamiento de datos de negocio por cliente
- **Estado:** POR VERIFICAR
- **Contexto:** Cada cliente debe tener datos de negocio aislados.
- **Opciones:** (a) base de datos por cliente; (b) esquema por cliente;
  (c) filas con `tenant_id` en base compartida.
- **Decisión:** Pendiente. Se documentará gestión de conexiones, roles, respaldos
  y límites una vez elegida.
- **Consecuencias:** Afecta a [`DATA_MODEL.md`](./DATA_MODEL.md) y
  [`OPERATIONS.md`](./OPERATIONS.md).

## ADR-013 · Fechas almacenadas en UTC
- **Estado:** CONFIRMADO
- **Contexto:** Consistencia entre zonas horarias.
- **Decisión:** Persistir en UTC; mostrar en zona configurada.
- **Consecuencias:** Conversión en capa de presentación.

## ADR-014 · Documentación antes que código
- **Estado:** CONFIRMADO
- **Contexto:** Evitar desarrollo sin especificación.
- **Decisión:** Completar `docs/EVAS_ADMIN/` antes de implementar (Fase 0).
- **Consecuencias:** Gating de fases por revisión humana.

---

## Preguntas que bloquean decisiones

1. ¿Existe ya un agente de operaciones o hay que construirlo? (ADR-007)
2. ¿Método de autenticación preferido y si habrá usuarios de cliente en el panel? (ADR-009)
3. ¿Cloudflare Tunnel es el mecanismo de publicación elegido? (ADR-010)
4. ¿Base por cliente, esquema por cliente o tenant_id compartido? (ADR-012)
5. Contenido y permisos reales del PostgreSQL existente (ADR-004).
