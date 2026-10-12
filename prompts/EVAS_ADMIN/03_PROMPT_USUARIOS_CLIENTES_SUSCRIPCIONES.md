# PASO 3 | Usuarios, clientes, productos y suscripciones

Lee `docs/EVAS_ADMIN/` y respeta el modelo de datos aprobado. Implementa estos módulos de forma incremental, con pruebas por módulo.

## Usuarios internos HAPMED
- Alta, edición, desactivación/reactivación.
- Roles iniciales sugeridos: Superadministrador, Operaciones, Atención al cliente y Solo lectura.
- Aplicar mínimo privilegio y prohibir la autoelevación de permisos.
- Hash de contraseña seguro si se implementa autenticación local; nunca guardar contraseñas en texto plano.

## Clientes y usuarios de clientes
- Alta, consulta, edición, suspensión y archivo lógico.
- Varios usuarios por cliente.
- Roles de cliente separados de los roles internos HAPMED.
- Aislamiento estricto entre empresas en cada endpoint y consulta.
- Registrar auditoría de cambios.

## Catálogo de EVAs
- Nombre, identificador estable, descripción, estado, versiones admitidas y requisitos de despliegue.
- No aceptar imágenes Docker ni parámetros arbitrarios desde el usuario.

## Suscripciones
- Planes mensuales, trimestrales y anuales.
- Fechas de inicio, renovación y vencimiento.
- Estados definidos en el dominio y transiciones válidas.
- Historial de renovaciones y cambios.
- Alertas configurables previas al vencimiento y para suscripciones vencidas.
- Fechas almacenadas en UTC y mostradas con la zona horaria configurada.
- No procesar pagos reales en esta fase.
- No suspender ni borrar instalaciones automáticamente sin política aprobada.

Implementa backend, frontend, migraciones locales y pruebas. No ejecutes migraciones en el PostgreSQL existente hasta que el usuario autorice la conexión y se confirme el destino. Actualiza `PRODUCT_REQUIREMENTS.md`, `DATA_MODEL.md` y `API_CONTRACTS.md`.
