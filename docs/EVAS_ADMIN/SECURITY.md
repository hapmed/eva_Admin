# SECURITY.md — Seguridad de EVAS Admin

**Estado:** Borrador inicial.
**Documentos relacionados:** [`ARCHITECTURE.md`](./ARCHITECTURE.md),
[`DOCKER_STANDARD.md`](./DOCKER_STANDARD.md),
[`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md).

## 1. Principios

1. **Mínimo privilegio** en personas, servicios y contenedores.
2. **Sin secretos** en Git, logs, documentación ni respuestas de API.
3. **Operaciones tipadas.** Nunca shell arbitrario desde HTTP.
4. **Aislamiento multi-tenant.** Los datos de un cliente no cruzan a otro.
5. **Todo lo crítico se audita.**
6. **Docker nunca expuesto** al frontend ni a la API general.

## 2. Modelo de amenazas (resumen)

| Amenaza | Vector | Mitigación |
|---------|--------|-----------|
| Ejecución arbitraria | Endpoint que invoca shell/Docker | Operaciones tipadas vía agente |
| Exposición del socket Docker | Montaje en API/FE | Sólo el agente lo usa, con permisos mínimos |
| Fuga de secretos | Logs, errores, Git | Logging saneado, `.env` fuera de Git, revisión |
| Mezcla de tenants | Consultas sin `client_id` | Filtro obligatorio + pruebas de aislamiento |
| Autoelevación | Cambio de roles por el propio usuario | Reglas de autorización server-side |
| Fuerza bruta | Login | Rate limiting + bloqueo progresivo |
| CSRF | Cookies de sesión | Token CSRF + SameSite ([`DECISIONS.md`](./DECISIONS.md#adr-009)) |
| Dependencias vulnerables | Imágenes/paquetes | Versiones fijas, escaneo, sin `latest` |

## 3. Autenticación

**Dual (ADR-009):**

- **Web (SPA):** cookie de sesión `HttpOnly`, `Secure` en producción,
  `SameSite=Lax|Strict`, más **token CSRF** en operaciones que mutan estado.
- **Integraciones/agente:** **token Bearer** de alcance mínimo, con expiración,
  rotación y revocación. Sólo se guarda su **hash** (`API_TOKEN`).
- Contraseñas con **hash seguro** (Argon2id o bcrypt). Nunca texto plano.
- (Propuesta) MFA para roles administrativos. [PROPUESTA]
- Bloqueo/limitación tras intentos fallidos; rate limiting en `/auth/*`.

## 4. Autorización

- Basada en **permisos** asignados por rol.
- Roles internos: `superadmin`, `operations`, `customer_care`, `read_only`.
- Roles de cliente **separados** de los internos.
- Verificación server-side en cada endpoint; nunca confiar en el frontend.
- Prohibida la **autoelevación** de privilegios.
- Operaciones destructivas (restore, upgrade, archive) requieren permiso
  específico + confirmación + auditoría.

## 5. Aislamiento multi-tenant

- **Una base de datos por cliente** (ADR-012): aísla los datos de negocio a
  nivel de base, no sólo de fila. La base administrativa (`evas_admin`) guarda
  sólo metadatos.
- Toda entidad de negocio lleva `client_id` y se filtra en cada consulta.
- El backend resuelve la conexión por cliente desde el gestor de secretos;
  nunca se expone al frontend.
- Los usuarios de cliente sólo acceden a su propia empresa.
- Se requieren **pruebas automáticas de aislamiento** entre clientes.

## 6. Seguridad de Docker

- **Nunca** se monta `/var/run/docker.sock` en `API` ni en `FE`.
- Sólo el **Agente de Operaciones** (componente propio del proyecto, ADR-007)
  accede a Docker, con:
  - Operaciones tipadas y enumeradas.
  - Acceso acotado a recursos con label `evas.managed_by`.
  - Sin imágenes, puertos, montajes ni privilegios arbitrarios.
  - Autenticación (token/mTLS con el backend) y auditoría por acción.
- **Modos:** `simulated` (no ejecuta cambios reales; local/MVP) y `real`
  (autorización humana + revisión de seguridad).
- Sin `privileged`, sin capacidades innecesarias ([`DOCKER_STANDARD.md`](./DOCKER_STANDARD.md)).

## 7. Red y transporte

- HTTPS obligatorio en producción.
- **CORS** restringido a orígenes configurados (vacío = ninguno).
- **Rate limiting** en rutas sensibles (`/auth/*` y operaciones) — implementado
  en memoria (ventana por IP); en multi-réplica usar almacén compartido.
- **Errores genéricos:** el backend nunca devuelve trazas ni detalles internos;
  las excepciones no controladas responden `500 {"error":{"code":"internal"}}`.
- Fallos del agente se registran como operación `failed` con código genérico
  (`agent_error`), sin exponer el mensaje.
- Exposición mínima de puertos; superficies internas sin publicar.
- Publicación vía Cloudflare Tunnel (ADR-010); sin tokens de Cloudflare en el
  código ni en la imagen.

## 8. Gestión de secretos

- Secretos por **variables de entorno** o gestor de secretos documentado.
- `.env` fuera de Git; `.env.example` con valores **ficticios**.
- Nunca registrar contraseñas, tokens, cookies ni cadenas de conexión.
- Los datos de negocio de clientes usan **referencias** a secretos
  (`SECRET_REFERENCE`), no valores ([`DATA_MODEL.md`](./DATA_MODEL.md)).

## 9. Logging y validación

- Errores sin detalles internos ni trazas al cliente.
- Validación estricta de entrada (Pydantic).
- Logs estructurados y **saneados**; tamaño y retención limitados.
- `request_id` para correlación, sin datos sensibles.

## 10. Auditoría

Se registran como mínimo: actor, instalación/entidad, operación, fecha y
resultado. Operaciones auditadas: login admin, cambios de rol/permiso, alta/baja
de clientes, cambios de suscripción, despliegue/actualización/restart, backup,
restore, y cambios de dominio/configuración.

## 11. Contenedores y dependencias

- Versiones **fijas**; nunca `latest` en producción.
- Procesos **no root** cuando sea viable.
- Healthchecks y rotación de logs.
- Sin `privileged` ni capacidades extra.

## 12. Respuesta a incidentes (resumen)

1. Contener (revocar tokens, aislar servicios).
2. Evaluar alcance vía auditoría.
3. Remediar y rotar secretos afectados.
4. Documentar y actualizar este archivo. Ver [`OPERATIONS.md`](./OPERATIONS.md).

## 13. Pendientes de confirmación

1. ¿MFA obligatorio para superadmin? [PROPUESTA]
2. Gestor de secretos definitivo (env vs Vault/Secrets Manager) y mapa de
   conexiones por cliente. [POR VERIFICAR]
3. Canal y política de notificación de incidentes.
4. Mecanismo exacto del canal backend⇄agente (mTLS vs token). [POR VERIFICAR]
