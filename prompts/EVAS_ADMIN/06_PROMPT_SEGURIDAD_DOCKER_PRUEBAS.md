# PASO 6 | Seguridad, contenedores y pruebas

Revisa la implementación completa y corrige problemas demostrables. No despliegues en producción.

Seguridad:
- Autenticación y autorización en backend.
- Protección CSRF si se usan cookies de sesión; cookies HttpOnly, Secure en producción y SameSite apropiado.
- CORS restringido a orígenes configurados.
- Rate limiting para rutas sensibles.
- Validación de entradas y errores sin detalles internos.
- Secretos mediante variables de entorno o sistema de secretos documentado.
- `.env` fuera de Git.
- Nunca registrar contraseñas, tokens, cookies ni cadenas de conexión.
- Auditoría para operaciones administrativas críticas.
- Dependencias e imágenes con versiones deliberadas, nunca `latest` en producción.
- Procesos no root cuando sea viable, healthchecks, rotación de logs y exposición mínima de puertos.
- No activar `privileged` ni capacidades innecesarias.

Pruebas:
- Unitarias y de API.
- Roles y permisos.
- Aislamiento entre clientes.
- Fechas y vencimientos.
- Migraciones en una base de prueba.
- Fallos del agente y operaciones repetidas.
- Lint, tipos y build frontend.

Archivos de operación:
- `Dockerfile` backend.
- `Dockerfile` frontend o build integrado documentado.
- `compose.yaml`.
- `.dockerignore`, `.gitignore`, `.env.example`.
- Healthchecks y rotación de logs.
- Documentación de backup, restore, actualización y rollback.

No modificar ni reiniciar el Docker PostgreSQL existente. No desplegar ni conectarse a producción sin autorización.
Actualiza `SECURITY.md`, `DOCKER_STANDARD.md`, `OPERATIONS.md` y `README.md`. Reporta solo pruebas que realmente se hayan ejecutado.
