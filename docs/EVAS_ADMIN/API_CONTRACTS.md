# API_CONTRACTS.md — Contratos de API de EVAS Admin

**Estado:** Borrador inicial. Endpoints propuestos, aún sin implementar.
**Base:** `/api/v1`
**Documentos relacionados:** [`DATA_MODEL.md`](./DATA_MODEL.md),
[`SECURITY.md`](./SECURITY.md), [`ARCHITECTURE.md`](./ARCHITECTURE.md).

## 1. Convenciones generales

| Aspecto | Convención |
|---------|-----------|
| Estilo | REST sobre HTTP/JSON |
| Versionado | Prefijo `/api/v1` |
| Autenticación | Dual (ADR-009): cookie de sesión (SPA) + token Bearer (integraciones/agente) |
| Paginación | `?page=1&page_size=25` con metadatos `total`, `page`, `page_size` |
| Orden | `?sort=field` / `?sort=-field` (descendente con `-`) |
| Filtrado | `?status=active&client_id=<uuid>` |
| Búsqueda | `?q=<texto>` |
| Idempotencia | Header `Idempotency-Key` en operaciones sensibles |
| Fechas | ISO-8601 en UTC (`2026-10-11T12:00:00Z`) |
| IDs | UUID |
| Documentación | OpenAPI autogenerada por FastAPI (`/docs`, `/openapi.json`) |

## 2. Formato de error

```json
{
  "error": {
    "code": "domain_conflict",
    "message": "El dominio ya está en uso por otra instalación.",
    "details": { "field": "fqdn" },
    "request_id": "0f7c2c1e-..."
  }
}
```

Códigos HTTP: `400` validación, `401` no autenticado, `403` sin permiso,
`404` no encontrado, `409` conflicto, `429` rate limit, `500` interno.

> Los errores **nunca** exponen detalles internos, trazas ni secretos.

## 3. Health & readiness

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/healthz` | Liveness (sin dependencias). |
| GET | `/readyz` | Readiness (comprueba BD y config, sin filtrar secretos). |

## 4. Autenticación y sesión

**Web (SPA):** cookie de sesión `HttpOnly`+`Secure`+`SameSite` + token CSRF.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/auth/csrf` | Obtener token CSRF. |
| POST | `/auth/login` | Iniciar sesión (emite cookie de sesión). |
| POST | `/auth/logout` | Cerrar sesión. |
| GET | `/auth/me` | Usuario actual y permisos. |
| POST | `/auth/password/change` | Cambio de contraseña. |

**Integraciones/agente (máquina-a-máquina):** token Bearer (ADR-009).

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/tokens` | `tokens:read` |
| POST | `/tokens` | `tokens:manage` |
| POST | `/tokens/{id}/revoke` | `tokens:manage` |

## 5. Usuarios internos HAPMED

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/users` | `users:read` |
| POST | `/users` | `users:write` |
| GET | `/users/{id}` | `users:read` |
| PATCH | `/users/{id}` | `users:write` |
| POST | `/users/{id}/deactivate` | `users:write` |
| POST | `/users/{id}/reactivate` | `users:write` |

**Roles y permisos**

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/roles` | `roles:read` |
| GET | `/permissions` | `roles:read` |
| PUT | `/roles/{id}/permissions` | `roles:manage` |

## 6. Clientes y usuarios de cliente

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/clients` | `clients:read` |
| POST | `/clients` | `clients:write` |
| GET | `/clients/{id}` | `clients:read` |
| PATCH | `/clients/{id}` | `clients:write` |
| POST | `/clients/{id}/suspend` | `clients:write` |
| POST | `/clients/{id}/archive` | `clients:write` |
| GET | `/clients/{id}/users` | `clients:read` |
| POST | `/clients/{id}/users` | `clients:write` |
| PATCH | `/clients/{id}/users/{userId}` | `clients:write` |

## 7. Catálogo de EVA

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/evas` | `evas:read` |
| POST | `/evas` | `evas:manage` |
| GET | `/evas/{id}` | `evas:read` |
| PATCH | `/evas/{id}` | `evas:manage` |
| GET | `/evas/{id}/versions` | `evas:read` |
| POST | `/evas/{id}/versions` | `evas:manage` |

> El usuario no elige imágenes ni parámetros arbitrales: sólo EVA y versiones
> registradas.

## 8. Planes y suscripciones

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/plans` | `plans:read` |
| POST | `/plans` | `plans:manage` |
| GET | `/subscriptions` | `subscriptions:read` |
| POST | `/subscriptions` | `subscriptions:write` |
| GET | `/subscriptions/{id}` | `subscriptions:read` |
| PATCH | `/subscriptions/{id}` | `subscriptions:write` |
| POST | `/subscriptions/{id}/renew` | `subscriptions:write` |
| POST | `/subscriptions/{id}/cancel` | `subscriptions:write` |
| GET | `/subscriptions/{id}/events` | `subscriptions:read` |

Los planes nuevos solo admiten `monthly` o `yearly`. Las respuestas de
suscripción incluyen el cálculo de tiempo (fechas en UTC):

| Campo | Descripción |
|-------|-------------|
| `days_total` | Días del periodo contratado (inicio → vencimiento). |
| `days_elapsed` | Días transcurridos desde el inicio. |
| `days_to_expiry` | Días restantes (0 si ya venció). |
| `days_overdue` | Días transcurridos desde el vencimiento. |
| `progress_percent` | Porcentaje transcurrido (0–100). |
| `is_expired` | `true` si la fecha de vencimiento ya pasó. |
| `expiring_soon` | `true` si vence en ≤ 14 días y está activa o en gracia. |

## 9. Instalaciones

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/installations` | `installations:read` |
| POST | `/installations` | `installations:write` |
| GET | `/installations/{id}` | `installations:read` |
| PATCH | `/installations/{id}` | `installations:write` |
| DELETE | `/installations/{id}` | `installations:write` |
| GET | `/installations/{id}/access` | `installations:write` |
| POST | `/installations/{id}/access` | `installations:write` |
| POST | `/installations/{id}/access/reset` | `installations:write` |
| GET | `/installations/{id}/services` | `installations:read` |
| GET | `/installations/{id}/health` | `installations:read` |
| POST | `/installations/{id}/restart` | `installations:operate` |
| POST | `/installations/{id}/upgrade` | `installations:upgrade` |
| POST | `/installations/{id}/health-check` | `installations:operate` |

`DELETE /installations/{id}` elimina el contenedor, el DNS/ingress, la base de
datos y los registros de la instalación. El cliente se conserva. Si el
contenedor no se puede eliminar, la operación se aborta sin borrar registros;
los fallos de DNS o base de datos se devuelven en `warnings`.

`GET /installations/{id}/access` devuelve las credenciales de administrador de
la EVA (`email`, `password`), almacenadas cifradas. `POST` las crea si faltan y
`POST /access/reset` genera una contraseña nueva. Requieren
`installations:write`; creación y regeneración quedan auditadas.

**Ejemplo — crear instalación (`POST /installations`)**

```json
{
  "client_id": "uuid",
  "eva_product_id": "uuid",
  "subscription_id": "uuid",
  "node_id": "uuid",
  "desired_version": "1.4.2",
  "primary_domain": "cliente.ejemplo.test"
}
```

**Ejemplo — actualización (`POST /installations/{id}/upgrade`)**

```json
{ "target_version": "1.5.0", "idempotency_key": "uuid", "confirm": true }
```

## 10. Dominios

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/domains` | `domains:read` |
| POST | `/domains` | `domains:write` |
| PATCH | `/domains/{id}` | `domains:write` |
| DELETE | `/domains/{id}` | `domains:write` |
| GET | `/domains/check?fqdn=` | `domains:read` |

> `PATCH /domains/{id}` cambia el FQDN, valida que sea único y actualiza el
> DNS/ingress de Cloudflare. El subdominio inicial de un cliente se sugiere a
> partir de su RFC (índice corto único).

## 11. Bases de datos (metadatos)

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/databases` | `databases:read` |
| POST | `/databases` | `databases:write` |
| GET | `/databases/{id}` | `databases:read` |
| POST | `/databases/{id}/backup` | `backups:request` |
| POST | `/databases/{id}/restore` | `backups:restore` |

> Nunca se devuelven credenciales. Sólo metadatos.

## 12. Monitoreo y operaciones

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/operations` | `operations:read` |
| GET | `/operations/{id}` | `operations:read` |
| GET | `/installations/{id}/logs` | `operations:read` |
| GET | `/installations/{id}/metrics` | `operations:read` |

> Logs **saneados**; tamaño y retención limitados ([`OPERATIONS.md`](./OPERATIONS.md)).

## 13. Auditoría y alertas

| Método | Ruta | Permiso |
|--------|------|---------|
| GET | `/audit-logs` | `audit:read` |
| GET | `/alerts` | `alerts:read` |
| POST | `/alerts/{id}/acknowledge` | `alerts:write` |
| POST | `/alerts/{id}/resolve` | `alerts:write` |

## 14. Contrato con el Agente de Operaciones

El backend **no** ejecuta Docker. Emite operaciones tipadas al agente —que es
**parte de este proyecto** (ADR-007)— por un canal autenticado (token/mTLS):

| Operación | Parámetros | Idempotente |
|-----------|-----------|-------------|
| `deploy_installation` | `installation_id`, `eva_version`, `config_ref`, `domain` | Sí |
| `upgrade_installation` | `installation_id`, `target_version` | Sí |
| `restart_service` | `installation_id`, `service_name` | Sí |
| `health_check` | `installation_id` | Sí |
| `request_backup` | `database_ref` | Sí |
| `request_restore` | `database_ref`, `backup_ref` | Sí |

- Sin parámetros arbitrarios (imágenes, puertos, montajes, privilegios).
- Autorización token/mTLS y auditoría por operación.
- **Modos:** `simulated` (responde sin cambios reales e indica `"simulated": true`)
  y `real` (requiere autorización humana y revisión de seguridad).

## 15. Pendientes de confirmación

1. Nombres definitivos de permisos.
2. Política de paginación y límites de tamaño.
3. ¿Se expone `/docs` en producción o sólo en entornos internos?
4. Contrato exacto (formato/puerto) del canal backend⇄agente. [POR VERIFICAR]
