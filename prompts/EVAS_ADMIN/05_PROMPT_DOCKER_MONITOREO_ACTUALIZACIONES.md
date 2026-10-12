# PASO 5 | Monitoreo Docker y actualizaciones seguras

Implementa el módulo de monitoreo, inicialmente con adaptador simulado. No conectes acciones a Docker real sin autorización expresa y revisión de seguridad.

Mostrar por instalación:
- Estado de aplicación y contenedores.
- Healthcheck cuando esté disponible.
- Versión deseada e instalada.
- Última comprobación y último despliegue.
- CPU/RAM si el agente proporciona métricas fiables.
- Estado de respaldo y alertas.
- Historial de eventos y logs saneados.

Operaciones permitidas, según rol:
- Consultar estado y logs.
- Reiniciar servicio permitido.
- Actualizar a una versión aprobada.
- Comprobar salud.
- Solicitar backup/restauración mediante flujo específico.

Toda actualización debe validar versión permitida, registrar la solicitud, comprobar requisitos, aplicar política de backup, ejecutar mediante agente restringido, esperar healthchecks y registrar resultado. Documentar rollback cuando sea posible.

Seguridad:
- No exponer `/var/run/docker.sock` al frontend ni a la API general.
- No ejecutar shell arbitrario.
- No aceptar imágenes, montajes, puertos o privilegios arbitrarios del usuario.
- No mostrar secretos en logs.
- Limitar tamaño y retención de logs.
- Requerir confirmación y autorización para acciones con impacto.
- Auditar actor, instalación, operación, fecha y resultado.

Pruebas para permisos, timeout, fallos, reintentos e idempotencia. Actualiza `DOCKER_STANDARD.md`, `OPERATIONS.md` y `SECURITY.md`.
