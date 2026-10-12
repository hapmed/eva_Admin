# PASO 4 | Instalaciones, configuración, dominios y bases de datos

Implementa la gestión lógica de instalaciones de clientes. No hagas aprovisionamiento real todavía.

Cada entidad debe ser independiente:
- Cliente.
- Suscripción.
- Aplicación EVA.
- Instalación/instancia.
- Servicios/contenedores de una instalación.
- Dominio/subdominio.
- Base de datos asignada.
- Configuración permitida y referencia a secretos.

Funciones:
- Crear y consultar instalaciones.
- Asociar instalación, cliente, producto y suscripción.
- Registrar estado, nodo/servidor, versión deseada e instalada y resultado de la última actualización.
- Registrar dominios y comprobar conflictos.
- Registrar metadatos de base de datos: motor, nombre lógico, host/nodo, estado y última copia de seguridad. No mostrar credenciales guardadas.
- Configuración validada contra un esquema permitido por cada EVA.
- Registro de operaciones y errores sin secretos.

PostgreSQL existente:
- No crear un nuevo contenedor PostgreSQL.
- No cambiar configuración, redes, volúmenes, roles, contraseñas ni versión del contenedor existente.
- No ejecutar comandos destructivos ni migraciones productivas.
- Documentar los datos de conexión mediante variables de entorno; nunca incluir valores reales en Git.
- Mantener la base de EVAS Admin separada de las bases de negocio de clientes.
- No crear bases ni usuarios en el servidor existente hasta confirmar qué contiene, quién lo utiliza y qué permisos hay disponibles.

Preparar un contrato para un agente de aprovisionamiento separado, con acciones tipadas y permisos mínimos. Si el agente no existe, usar un adaptador simulado que indique claramente que no hizo cambios reales.
Añadir pruebas de aislamiento, conflicto de dominio, idempotencia y errores. Actualizar `POSTGRES_EXISTING_INSTANCE.md`, `DATA_MODEL.md`, `API_CONTRACTS.md` y `SECURITY.md`.
