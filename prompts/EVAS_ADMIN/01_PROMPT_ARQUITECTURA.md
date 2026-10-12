# PASO 1 | Arquitectura y plan

Lee primero toda la documentación de `docs/EVAS_ADMIN/` y el código existente. No empieces si detectas contradicciones importantes; documéntalas y pregunta lo necesario.

Actualiza los documentos de arquitectura para reflejar el estado real del repositorio y define:
- Componentes y límites de confianza.
- Estructura de carpetas para FastAPI y SvelteKit.
- Entidades y relaciones.
- Endpoints por módulo.
- Autenticación, roles y autorización.
- Pruebas, observabilidad, backups y recuperación.
- Plan por fases con criterios de aceptación.
- Diagrama Mermaid del flujo de una instalación nueva y de una actualización.

Decisiones de arquitectura:
- Python + FastAPI para backend.
- SvelteKit + TypeScript para frontend.
- Tailwind CSS y componentes Svelte mantenibles.
- SQLAlchemy + Alembic.
- PostgreSQL existente, sujeto a inspección y confirmación. No crear ni alterar el contenedor automáticamente.
- Docker Compose para empaquetar la aplicación.
- Una base administrativa independiente de las bases de negocio de los clientes.
- Cada cliente debe tener datos de negocio aislados. La estrategia inicial puede ser una base independiente por cliente, siempre que se documente la gestión de conexiones, roles, respaldos y límites.
- Modelar por separado cliente, suscripción, producto EVA, instalación, servicios/contenedores, dominio y base de datos.
- Evitar microservicios innecesarios al inicio. Mantener módulos claros y límites internos definidos.
- Las operaciones Docker se realizarán a través de un servicio restringido, no desde endpoints arbitrarios del panel.

No implementes toda la aplicación en esta fase. Entrega decisiones, riesgos, diagrama, modelo de datos, endpoints y un plan ejecutable. Actualiza `ARCHITECTURE.md`, `DATA_MODEL.md`, `API_CONTRACTS.md`, `SECURITY.md`, `IMPLEMENTATION_PLAN.md` y `DECISIONS.md`.
