# EVAS Admin — Documentación de especificación

**Producto:** EVAS Admin (panel de administración de HAPMED)
**Repositorio:** <https://github.com/hapmed/eva_Admin>
**Estado:** Especificación vigente. Fases 0-4 completadas (identidad, comercial e infraestructura lógica).
**Última actualización:** 2026-10-11

> Esta carpeta contiene la especificación funcional y técnica que guiará el
> desarrollo. La documentación se escribe **antes** del código y se mantiene
> sincronizada con él. No contiene secretos, credenciales, IP reales ni datos
> personales.

## 1. Qué es EVAS Admin

EVAS (Ecosistema de Aplicaciones Verticales) son las aplicaciones de negocio que
HAPMED entrega a sus clientes, desplegadas como contenedores Docker. **EVAS Admin**
es el panel interno desde el que HAPMED administra el ciclo de vida comercial y
operativo de esas instalaciones:

- Clientes/empresas y sus usuarios.
- Catálogo de aplicaciones EVA y sus versiones.
- Suscripciones, planes, renovaciones y vencimientos.
- Instalaciones (instancias) por cliente, sus dominios y sus bases de datos.
- Monitoreo de estado (healthchecks, logs saneados, métricas disponibles).
- Actualizaciones controladas y operaciones de respaldo/restauración.
- Auditoría y alertas.

EVAS Admin es una herramienta **interna de HAPMED**. No es el producto que usan
los clientes finales.

## 2. Alcance

**Dentro del alcance (MVP):**

- Gestión (CRUD lógico) de clientes, usuarios internos, usuarios de cliente,
  catálogo de EVA, planes, suscripciones, instalaciones, dominios y metadatos de
  bases de datos.
- Dashboard con resumen operativo.
- Monitoreo **con el agente en modo `simulated`** en la primera iteración.
- Auditoría de operaciones administrativas.
- Interfaz responsive (móvil, tablet, escritorio).

**Fuera del alcance (MVP):**

- Procesamiento real de pagos.
- Aprovisionamiento real sobre Docker en esta etapa (se hará mediante un agente
  restringido y tras autorización explícita).
- Ejecución de migraciones contra el PostgreSQL productivo existente.
- PWA como requisito bloqueante (se evalúa como mejora posterior).

## 3. Stack y arquitectura objetivo

| Capa | Tecnología | Estado |
|------|------------|--------|
| Backend | Python + FastAPI | [CONFIRMADO] |
| Frontend | SvelteKit + TypeScript | [CONFIRMADO] |
| Estilos | Tailwind CSS + componentes compatibles SvelteKit | [CONFIRMADO] |
| ORM / migraciones | SQLAlchemy + Alembic | [CONFIRMADO] |
| Base administrativa | PostgreSQL (instancia **existente**) | [CONFIRMADO] |
| Despliegue de apps | Docker Compose en Linux | [CONFIRMADO] |
| Publicación | Cloudflare Tunnel | [CONFIRMADO] |
| UI | Responsive móvil/tablet/PC | [CONFIRMADO] |
| Lenguaje de diseño | Apple HIG (skill `apple-design-skill`) + marca HAPMED | [PROPUESTA] |

Ver detalle en [`ARCHITECTURE.md`](./ARCHITECTURE.md) y
[`UX_DESIGN_SYSTEM.md`](./UX_DESIGN_SYSTEM.md).

### Recursos de marca

Los activos de marca están en [`brand/`](../../brand/) (símbolo en color y
monocromo, icono de app, favicon, apple-touch-icon y og-image). Referencia de
tono y estructura: <https://www.hapmed.qzz.io/>. Reglas de uso en
[`UX_DESIGN_SYSTEM.md`](./UX_DESIGN_SYSTEM.md#1-identidad-de-marca).

## 4. Restricción crítica: PostgreSQL existente

> **Ya existe un contenedor Docker con PostgreSQL. NO se crea otro y NO se
> modifica el existente automáticamente.**

- La base administrativa de EVAS debe ser **independiente** de las bases de
  negocio de clientes.
- La conexión se resuelve mediante **variables de entorno**.
- No se crean bases ni roles en el servidor existente hasta confirmar permisos y
  capacidad.
- Procedimiento de inspección segura y preguntas pendientes en
  [`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md).

## 5. Estructura de carpetas prevista del repositorio

```
EVA_Admin/
├─ docs/EVAS_ADMIN/        # Esta documentación (especificación)
├─ prompts/EVAS_ADMIN/     # Prompts de especificación por fase (PASO 0..7)
├─ backend/                # FastAPI + SQLAlchemy + Alembic  (a crear)
├─ frontend/               # SvelteKit + TypeScript          (a crear)
├─ ops/                    # Dockerfiles, compose.yaml, scripts operativos (a crear)
└─ .env.example            # Variables de entorno ficticias  (a crear)
```

La estructura concreta de `backend/` y `frontend/` se define en
[`ARCHITECTURE.md`](./ARCHITECTURE.md).

## 6. Índice de documentación

| Documento | Contenido |
|-----------|-----------|
| [`README.md`](./README.md) | Este archivo. Visión general e índice. |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Componentes, límites de confianza, estructura, flujos. |
| [`PRODUCT_REQUIREMENTS.md`](./PRODUCT_REQUIREMENTS.md) | Módulos, historias y criterios de aceptación. |
| [`DATA_MODEL.md`](./DATA_MODEL.md) | Entidades, relaciones y reglas. |
| [`API_CONTRACTS.md`](./API_CONTRACTS.md) | Convenciones y endpoints por módulo. |
| [`SECURITY.md`](./SECURITY.md) | Modelo de amenazas, auth, secretos, auditoría. |
| [`UX_DESIGN_SYSTEM.md`](./UX_DESIGN_SYSTEM.md) | Principios de diseño, tokens, componentes. |
| [`DOCKER_STANDARD.md`](./DOCKER_STANDARD.md) | Estándares de contenedores y Compose. |
| [`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md) | Instancia PostgreSQL preexistente. |
| [`OPERATIONS.md`](./OPERATIONS.md) | Backups, actualizaciones, logs, runbooks. |
| [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) | Fases y criterios de aceptación. |
| [`DECISIONS.md`](./DECISIONS.md) | Registro de decisiones (ADR). |

## 7. Convenciones del repositorio

- **Idioma:** documentación y UI en español. Código e identificadores en inglés.
- **Secretos:** nunca en Git, logs ni documentación. Ver [`SECURITY.md`](./SECURITY.md).
- **Fechas:** almacenar en UTC, mostrar en la zona horaria configurada.
- **Marcado de estado:** todo dato no confirmado se etiqueta como
  `[POR VERIFICAR]`, `[PROPUESTA]` o `[CONFIRMADO]`.
- **Diagramas:** Mermaid embebido en Markdown.

## 8. Glosario

| Término | Significado |
|---------|-------------|
| **Cliente** | Empresa a la que se le presta un servicio EVA. |
| **Usuario interno** | Empleado de HAPMED que opera EVAS Admin. |
| **Usuario de cliente** | Usuario final perteneciente a un cliente. |
| **EVA / Aplicación EVA** | Producto de software entregable (p. ej. una vertical). |
| **Instalación / Instancia** | Despliegue concreto de una EVA para un cliente. |
| **Suscripción** | Acuerdo comercial (plan + vigencia) que habilita una instalación. |
| **Nodo / Servidor** | Host Linux con Docker donde corren instalaciones. |
| **Agente de operaciones** | Servicio restringido que ejecuta operaciones tipadas sobre Docker. |

## 9. Cómo empezar a desarrollar

1. Leer este README y [`ARCHITECTURE.md`](./ARCHITECTURE.md).
2. Revisar [`DECISIONS.md`](./DECISIONS.md) y resolver los puntos `[POR VERIFICAR]`.
3. Confirmar la información de la instancia PostgreSQL existente
   ([`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md)).
4. Seguir [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) fase por fase.
