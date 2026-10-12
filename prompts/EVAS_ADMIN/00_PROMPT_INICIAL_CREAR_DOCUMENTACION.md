# PASO 0 | Crear la documentación del proyecto antes de programar

Copia y ejecuta este prompt en OpenCode desde la raíz del repositorio destinado a EVAS Admin.

Actúa como arquitecto y responsable técnico de HAPMED. Tu primera tarea NO es desarrollar la aplicación: es crear dentro del repositorio los archivos Markdown de especificación que guiarán el desarrollo.

## Instrucciones
1. Inspecciona la raíz del repositorio y los archivos existentes antes de crear o modificar cualquier cosa.
2. No sobrescribas documentación existente sin leerla y explicar el motivo.
3. Crea la carpeta `docs/` y, dentro de ella, `docs/EVAS_ADMIN/`.
4. Crea los siguientes archivos Markdown usando los prompts de especificación que están disponibles en la carpeta `prompts/EVAS_ADMIN/`, si existen:
   - `docs/EVAS_ADMIN/README.md`
   - `docs/EVAS_ADMIN/ARCHITECTURE.md`
   - `docs/EVAS_ADMIN/PRODUCT_REQUIREMENTS.md`
   - `docs/EVAS_ADMIN/DATA_MODEL.md`
   - `docs/EVAS_ADMIN/API_CONTRACTS.md`
   - `docs/EVAS_ADMIN/SECURITY.md`
   - `docs/EVAS_ADMIN/UX_DESIGN_SYSTEM.md`
   - `docs/EVAS_ADMIN/DOCKER_STANDARD.md`
   - `docs/EVAS_ADMIN/POSTGRES_EXISTING_INSTANCE.md`
   - `docs/EVAS_ADMIN/OPERATIONS.md`
   - `docs/EVAS_ADMIN/IMPLEMENTATION_PLAN.md`
   - `docs/EVAS_ADMIN/DECISIONS.md`
5. Si los prompts no están en el repositorio, usa los requisitos incluidos en este prompt y en los mensajes del usuario disponibles en el contexto. No inventes detalles de infraestructura.
6. Escribe documentación específica, accionable y coherente entre archivos. Usa Mermaid para diagramas cuando ayude.
7. Marca claramente las decisiones confirmadas, las propuestas y los datos que todavía hay que verificar.
8. No incluyas secretos, contraseñas, tokens, cadenas de conexión reales, IP privadas, ni datos personales reales.
9. No ejecutes migraciones, no crees bases de datos, no alteres contenedores y no despliegues nada.
10. Al finalizar, muestra un resumen de cada archivo creado y señala contradicciones o decisiones que requieran confirmación.

## Arquitectura objetivo
- Backend: Python + FastAPI.
- Frontend: SvelteKit + TypeScript.
- Estilos: Tailwind CSS y componentes compatibles con SvelteKit.
- ORM y migraciones: SQLAlchemy + Alembic.
- Base administrativa: PostgreSQL.
- Despliegue de aplicaciones: Docker Compose en Linux.
- Publicación: preparado para Cloudflare Tunnel, sin exigir configuración productiva en esta etapa.
- Interfaz responsive para móvil, tablet y PC; evaluar PWA como mejora, sin convertirla en requisito que retrase el MVP.

## PostgreSQL existente: requisito obligatorio
Ya existe un contenedor Docker con PostgreSQL. No crees otro contenedor PostgreSQL ni cambies el existente automáticamente.
Primero documenta cómo inspeccionar de forma segura su nombre, versión, redes, volúmenes, bases, roles y aplicaciones consumidoras, sin imprimir contraseñas ni secretos.
La aplicación debe usar variables de entorno para conectarse.
La base administrativa de EVAS debe ser independiente de las bases de datos de negocio de los clientes.
No asumas que se puede crear una base o un usuario hasta confirmar permisos y capacidad del servidor existente.
No ejecutes comandos que borren, reinicien, actualicen o modifiquen el contenedor actual.
Si faltan datos, registra placeholders y formula preguntas concretas.

## Módulos funcionales
- Dashboard.
- Usuarios internos HAPMED, roles y permisos.
- Clientes/empresas y usuarios de cada cliente.
- Catálogo de aplicaciones EVA.
- Suscripciones, planes, renovaciones y vencimientos.
- Instalaciones/instancias por cliente.
- Dominios y subdominios.
- Bases de datos asignadas a las instalaciones.
- Estado de Docker, healthchecks, registros y métricas disponibles.
- Actualizaciones controladas.
- Auditoría, alertas y operaciones de respaldo/restauración.

## Reglas de seguridad
- No exponer el socket Docker a la interfaz ni a la API general.
- No permitir comandos shell arbitrarios desde solicitudes web.
- Diseñar un agente/servicio de operaciones separado, de permisos mínimos y con operaciones tipadas.
- Las operaciones destructivas requieren permisos específicos, confirmación y auditoría.
- No mezclar datos de negocio entre clientes.
- No guardar secretos en Git ni registrarlos en logs.
