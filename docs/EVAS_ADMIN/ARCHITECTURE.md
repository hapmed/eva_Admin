# ARCHITECTURE.md — Arquitectura de EVAS Admin

**Estado:** Propuesta inicial de arquitectura. Sujeta a confirmación en Fase 1.
**Documentos relacionados:** [`DATA_MODEL.md`](./DATA_MODEL.md),
[`API_CONTRACTS.md`](./API_CONTRACTS.md), [`SECURITY.md`](./SECURITY.md),
[`DOCKER_STANDARD.md`](./DOCKER_STANDARD.md).

## 1. Principios de arquitectura

1. **Simplicidad primero.** Monolito modular, no microservicios, en el MVP.
2. **Límites de confianza explícitos.** El panel nunca ejecuta Docker directo.
3. **Aislamiento multi-tenant.** Ningún dato de negocio cruza entre clientes.
4. **Seguro por defecto.** Mínimo privilegio, secretos fuera del código.
5. **Preexistente se respeta.** El PostgreSQL existente y los contenedores
   actuales no se crean, reinician ni modifican automáticamente.
6. **Operaciones tipadas.** Sin shell arbitrario expuesto a HTTP.

## 2. Diagrama de contexto y límites de confianza

```mermaid
flowchart TB
  subgraph Z0["Zona 0 · Usuarios"]
    INT["Equipo HAPMED (interno)"]
    CLI["Usuarios de cliente"]
  end

  subgraph Z1["Zona 1 · Borde (futuro)"]
    CF["Cloudflare Tunnel [PROPUESTA]"]
  end

  subgraph Z2["Zona 2 · EVAS Admin (Docker Compose)"]
    FE["Frontend SvelteKit"]
    API["Backend FastAPI"]
    AG["Agente de Operaciones (restringido)"]
  end

  subgraph Z3["Zona 3 · Preexistente / Clientes (NO autogestionado en MVP)"]
    PG[("PostgreSQL existente (contenedor Docker)")]
    NODES["Nodos Docker de instalaciones"]
  end

  INT -->|HTTPS| CF
  CLI -->|HTTPS| CF
  CF --> FE
  FE -->|REST/JSON| API
  API -->|SQLAlchemy| PG
  API -->|"operaciones tipadas (mTLS/token)"| AG
  AG -->|"API Docker acotada"| NODES
  API -.->|"solo lectura de metadatos"| NODES
```

**Fronteras de confianza:**

- **Z1→Z2:** terminación TLS y publicación. El acceso al panel requiere
  autenticación.
- **Z2 internia:** `FE` no habla nunca con Docker ni con la BD directamente;
  sólo con `API`.
- **Z2→Z3:** `API` sí puede leer la BD administrativa, pero **nunca** ejecuta
  comandos Docker. Sólo `AG` (agente) puede tocar Docker, y sólo mediante
  operaciones tipadas y autorizadas.
- **Sin acceso:** `/var/run/docker.sock` no se monta en `FE` ni en `API`.

## 3. Componentes

### 3.1 Frontend (SvelteKit + TypeScript)

- SPA/SSR de administración. Consume la API REST.
- Tailwind CSS para estilos.
- Responsive móvil/tablet/PC.
- Sin lógica de negocio sensible: sólo presentación y validación de formularios.

### 3.2 Backend (FastAPI)

- API REST versionada (`/api/v1`).
- Autenticación y autorización por rol/permiso.
- Lógica de dominio (clientes, suscripciones, instalaciones, etc.).
- Acceso a la BD administrativa vía SQLAlchemy; migraciones con Alembic.
- Emite **solicitudes de operación** al agente; no ejecuta Docker.
- Auditoría y alertas.

### 3.3 Agente de Operaciones (servicio separado, restringido)

- Superficie mínima, operaciones **tipadas** (p. ej. `restart_installation`,
  `upgrade_installation`, `get_health`, `request_backup`).
- Permisos mínimos sobre la API Docker.
- No acepta imágenes, puertos, montajes ni privilegios arbitrarios.
- Requiere autorización (token/mTLS) y registra toda acción.
- **En MVP:** se implementa un **adaptador simulado** que no realiza cambios
  reales y lo indica explícitamente.

### 3.4 PostgreSQL existente

- Aloja la **base administrativa** de EVAS (independiente de las bases de
  negocio de clientes).
- Tratado como recurso preexistente. Ver
  [`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md).

## 4. Estructura de carpetas

### 4.1 Backend (propuesta)

```
backend/
├─ app/
│  ├─ main.py                # Bootstrap FastAPI
│  ├─ core/
│  │  ├─ config.py           # Settings desde variables de entorno
│  │  ├─ security.py         # Hashing, tokens, dependencias de auth
│  │  └─ logging.py          # Logging saneado
│  ├─ db/
│  │  ├─ base.py             # Declarative Base, engine, session
│  │  └─ session.py
│  ├─ models/                # Modelos SQLAlchemy (ver DATA_MODEL.md)
│  ├─ schemas/               # Pydantic (request/response)
│  ├─ api/
│  │  └─ v1/
│  │     ├─ router.py
│  │     └─ endpoints/       # Un módulo por dominio
│  ├─ services/              # Lógica de dominio
│  ├─ agents/                # Cliente del agente de operaciones + mock
│  └─ audit/                 # Registro de auditoría
├─ alembic/                  # Migraciones (no se ejecutan en prod sin autorización)
├─ tests/
├─ pyproject.toml
└─ Dockerfile
```

### 4.2 Frontend (propuesta)

```
frontend/
├─ src/
│  ├─ lib/
│  │  ├─ api/                # Cliente HTTP tipado
│  │  ├─ components/         # Tablas, filtros, diálogos, estados
│  │  ├─ stores/             # Estado de sesión y UI
│  │  └─ styles/             # Tailwind y tokens
│  ├─ routes/
│  │  ├─ (auth)/
│  │  ├─ dashboard/
│  │  ├─ clientes/
│  │  ├─ usuarios/
│  │  ├─ evas/
│  │  ├─ suscripciones/
│  │  ├─ instalaciones/
│  │  ├─ dominios/
│  │  ├─ bases-de-datos/
│  │  ├─ monitoreo/
│  │  └─ auditoria/
├─ static/
├─ svelte.config.js
├─ tailwind.config.js
└─ Dockerfile
```

## 5. Modelo de dominio (resumen)

Entidades separadas y relacionadas: **Cliente**, **Suscripción**, **EVA**,
**Instalación**, **Servicio/Contenedor**, **Dominio** y **Base de datos**, además
de usuarios, roles, auditoría y operaciones. Detalle en
[`DATA_MODEL.md`](./DATA_MODEL.md).

```mermaid
flowchart LR
  CLIENT --> SUBSCRIPTION
  SUBSCRIPTION --> INSTALLATION
  EVA --> INSTALLATION
  INSTALLATION --> SERVICE
  INSTALLATION --> DOMAIN
  INSTALLATION --> DATABASE
```

## 6. Autenticación y autorización (resumen)

- **Internos HAPMED:** roles Superadministrador, Operaciones, Atención al
  cliente y Solo lectura.
- **Usuarios de cliente:** roles separados de los internos.
- Autorización por **permiso** (no sólo por rol).
- Sesión por cookie HttpOnly + CSRF, o token; a decidir en
  [`DECISIONS.md`](./DECISIONS.md). Detalle en [`SECURITY.md`](./SECURITY.md).

## 7. Flujos principales

### 7.1 Alta de instalación nueva

```mermaid
sequenceDiagram
  actor Op as Operaciones HAPMED
  participant FE as Frontend
  participant API as Backend FastAPI
  participant AG as Agente (mock en MVP)
  participant PG as PostgreSQL admin

  Op->>FE: Crear instalación (cliente, EVA, versión, dominio)
  FE->>API: POST /installations
  API->>PG: Valida cliente, suscripción, EVA y dominio
  API-->>API: Comprueba conflicto de dominio (idempotente)
  API->>AG: deploy_installation (operación tipada)
  AG-->>API: result (MVP: simulado, sin cambios reales)
  API->>PG: Registra instalación + operación + auditoría
  API-->>FE: 201 Created (estado = pending/active)
```

### 7.2 Actualización controlada

```mermaid
sequenceDiagram
  actor Op as Operaciones HAPMED
  participant FE as Frontend
  participant API as Backend FastAPI
  participant AG as Agente (mock en MVP)
  participant PG as PostgreSQL admin

  Op->>FE: Solicitar actualización a versión aprobada
  FE->>API: POST /installations/{id}/upgrade
  API->>API: Valida versión permitida y permisos
  API->>PG: Registra solicitud de operación (auditoría)
  API->>AG: upgrade_installation(target_version)
  AG->>AG: (MVP) simulacro; (real) aplica política de backup
  AG-->>API: result + healthcheck
  API->>PG: Registra resultado, versión instalada, alertas
  API-->>FE: Estado final + eventos
```

## 8. Observabilidad

- Logs estructurados y **saneados** (sin secretos) con retención y rotación
  definidas ([`OPERATIONS.md`](./OPERATIONS.md)).
- Endpoints de salud: `/healthz` (liveness) y `/readyz` (readiness) sin filtrar
  secretos.
- Métricas disponibles si el agente las provee (CPU/RAM). Ver [`DOCKER_STANDARD.md`](./DOCKER_STANDARD.md).
- Alertas configurables (vencimientos, healthcheck fallido, backup ausente).

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Exposición accidental del socket Docker | Nunca montarlo en API/FE; sólo agente restringido. |
| Fuga de secretos en logs | Logging saneado, revisión, `.env` fuera de Git. |
| Mezcla de datos entre clientes | Filtro por tenant obligatorio + pruebas de aislamiento. |
| Impacto sobre PostgreSQL existente | Sólo lectura de metadatos; sin DDL sin autorización. |
| Ejecución de comandos arbitrarios | Operaciones tipadas con parámetros validados. |

## 10. Pendientes de confirmación

- Método de autenticación definitivo (cookie+CSRF vs token). Ver [`DECISIONS.md`](./DECISIONS.md).
- Estrategia de aislamiento de datos de negocio (base por cliente vs esquema por
  cliente). [POR VERIFICAR]
- Existencia y contrato real del agente de operaciones. [POR VERIFICAR]
- Detalles de la instancia PostgreSQL existente. Ver [`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md).
