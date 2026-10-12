# DECISIONS.md — Registro de decisiones de arquitectura (ADR)

Formato: `ID · Estado · Decisión · Contexto · Consecuencias`.
Estados: **CONFIRMADO**, **PROPUESTA**, **POR VERIFICAR**, **RECHAZADO**.

**Fase 1 (Arquitectura y plan):** completada. Se cerraron las decisiones
ADR-007, ADR-009, ADR-010 y ADR-012, y se añadieron ADR-015 y ADR-016.

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
- **Consecuencias:** Distintas conexiones, roles y respaldos. Ver ADR-012.

## ADR-006 · Monolito modular en lugar de microservicios
- **Estado:** CONFIRMADO
- **Contexto:** Equipo pequeño; MVP rápido.
- **Decisión:** Un backend modular con límites internos claros. El agente de
  operaciones es el único servicio separado (ADR-007).
- **Consecuencias:** Menos complejidad operativa; el agente se puede desplegar
  aparte.

## ADR-007 · Agente de operaciones propio, separado y restringido
- **Estado:** CONFIRMADO
- **Contexto:** No exponer el socket Docker a la API ni al frontend.
- **Decisión:** Las operaciones Docker sólo se ejecutan mediante un servicio con
  operaciones **tipadas** y permisos mínimos. El agente **se construye como parte
  de este proyecto** (carpeta `agent/`), no se asume preexistente.
- **Consecuencias:** El agente es un entregable del repositorio. Soporta modo
  `simulated` (sin cambios reales; para local/MVP) y modo `real` (requiere
  autorización humana y revisión de seguridad). El canal backend⇄agente se
  autentica con token/mTLS.

## ADR-008 · Operaciones de Docker vía operaciones tipadas, sin shell
- **Estado:** CONFIRMADO
- **Contexto:** Riesgo de ejecución arbitraria desde HTTP.
- **Decisión:** Prohibido el shell arbitrario; sólo operaciones enumeradas.
- **Consecuencias:** Mayor seguridad; menos flexibilidad.

## ADR-009 · Autenticación dual: cookie para la web + token para integraciones
- **Estado:** CONFIRMADO
- **Contexto:** La SPA necesita sesión de navegador; el agente e integraciones
  necesitan acceso máquina-a-máquina.
- **Decisión:** **Ambos** métodos:
  - **Web (SPA):** cookie de sesión `HttpOnly` + `Secure` + `SameSite` con
    protección **CSRF**.
  - **Integraciones/agente:** **token** Bearer de alcance mínimo, con rotación y
    revocación.
- **Consecuencias:** CORS restringido; dos superficies de autenticación y dos
  políticas de permisos. Ver [`SECURITY.md`](./SECURITY.md) y
  [`API_CONTRACTS.md`](./API_CONTRACTS.md).

## ADR-010 · Publicación mediante Cloudflare Tunnel
- **Estado:** CONFIRMADO
- **Contexto:** Exponer el panel sin abrir puertos.
- **Decisión:** Publicar mediante **Cloudflare Tunnel**, separado del contenedor
  de la app cuando la arquitectura lo permita. No se exige configuración
  productiva en las fases iniciales.
- **Consecuencias:** HTTPS gestionado; DNS y políticas se definen fuera del
  repositorio; sin tokens de Cloudflare en el código ni en la imagen.

## ADR-011 · PWA como mejora opcional, no bloqueante
- **Estado:** CONFIRMADO
- **Contexto:** Podría aportar valor móvil, pero no debe retrasar el MVP.
- **Decisión:** Evaluar PWA tras el MVP.
- **Consecuencias:** Sin manifest/service worker en el MVP.

## ADR-012 · Aislamiento de datos de negocio: una base de datos por cliente
- **Estado:** CONFIRMADO
- **Contexto:** Cada cliente debe tener datos de negocio aislados.
- **Decisión:** **Una base de datos PostgreSQL por cliente**, independiente de la
  base administrativa de EVAS y de las demás bases de clientes.
- **Consecuencias:** Máximo aislamiento; requiere gestión de conexiones,
  credenciales/roles por base, respaldos y límites independientes. Afecta a
  [`DATA_MODEL.md`](./DATA_MODEL.md), [`OPERATIONS.md`](./OPERATIONS.md) y
  [`ARCHITECTURE.md`](./ARCHITECTURE.md). No se crean bases reales sin
  autorización.

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

## ADR-015 · Estrategia de pruebas
- **Estado:** CONFIRMADO
- **Contexto:** Verificar dominio, seguridad, aislamiento y operaciones.
- **Decisión:**
  - **Backend:** `pytest` (unitarias y de API con `TestClient`), pruebas de
    aislamiento multi-tenant, migraciones en base efímera, contrato del agente
    con mock e idempotencia.
  - **Frontend:** `svelte-check` (tipos), `vitest` (unidades), lint.
  - **CI:** lint + typecheck + tests antes del build de imágenes.
- **Consecuencias:** Cada fase reporta pruebas **realmente ejecutadas**.

## ADR-016 · Observabilidad y recuperación
- **Estado:** CONFIRMADO
- **Contexto:** Necesidad de operar y recuperar el sistema con seguridad.
- **Decisión:** Logs estructurados y saneados con rotación/retención;
  `/healthz` y `/readyz`; métricas por instalación si el agente las provee;
  alertas configurables; backups por base (administrativa y por cliente) con
  restauración auditada y rollback documentado.
- **Consecuencias:** Ver [`OPERATIONS.md`](./OPERATIONS.md).

---

## Decisiones resueltas en Fase 1

- **Agente de operaciones:** se construye en este proyecto (ADR-007).
- **Autenticación:** dual — cookie para la web + token para integraciones (ADR-009).
- **Publicación:** Cloudflare Tunnel (ADR-010).
- **Aislamiento de datos:** una base de datos por cliente (ADR-012).
- **Pruebas y observabilidad:** definidas (ADR-015, ADR-016).

## Preguntas pendientes

1. Contenido y permisos reales del PostgreSQL existente (ADR-004) —
   [`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md).
2. ¿Los usuarios de cliente acceden al panel o es sólo interno? (alcance de
   ADR-009).
3. Gestor de secretos definitivo (env vs Vault/Secrets Manager). [POR VERIFICAR]
4. Canal de notificación de alertas e incidentes. [POR VERIFICAR]
