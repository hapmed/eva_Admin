# DOCKER_STANDARD.md — Estándares de contenedores y Compose

**Estado:** Borrador inicial.
**Aplica a:** (a) la propia EVAS Admin y (b) cada aplicación EVA desplegada.
**Documentos relacionados:** [`ARCHITECTURE.md`](./ARCHITECTURE.md),
[`SECURITY.md`](./SECURITY.md), [`OPERATIONS.md`](./OPERATIONS.md),
[`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md).

## 1. Regla previa absoluta: PostgreSQL existente

> **Existe un contenedor Docker con PostgreSQL. NO se crea otro, NO se reinicia,
> NO se actualiza y NO se modifican sus redes, volúmenes, roles ni contraseñas.**

Ver [`POSTGRES_EXISTING_INSTANCE.md`](./POSTGRES_EXISTING_INSTANCE.md). La
`compose.yaml` de EVAS Admin **no** debe declarar ningún servicio PostgreSQL.

## 2. Estándares para imágenes de aplicaciones EVA

- **Versiones fijas.** Prohibido `latest` en producción (usar tags semver o
  digest).
- **Usuario no root** cuando sea viable.
- **Sin `privileged`** ni capacidades añadidas innecesarias.
- **Filesystem de sólo lectura** cuando sea posible; `tmpfs` para lo necesario.
- Imagen mínima; sin herramientas de compilación en la imagen final.
- **Healthcheck** obligatorio (comando o endpoint).
- Variables de configuración por entorno; **sin secretos** incrustados.

## 3. Convenciones de nombres y etiquetas (labels)

- Contenedores: `eva_<cliente>_<app>` (referencia lógica).
- Redes por instalación/cliente: `eva_<cliente>_net`.
- Volúmenes: `eva_<cliente>_<app>_data`.
- Labels recomendadas:

| Label | Uso |
|-------|-----|
| `evas.installation_id` | Identificador lógico de la instalación |
| `evas.client_ref` | Referencia lógica del cliente |
| `evas.eva_code` | Código de la EVA |
| `evas.version` | Versión desplegada |
| `evas.managed_by` | `evas-admin` |

> Estas labels permiten al agente identificar recursos **sin** exponer datos
> sensibles ni aceptar nombres arbitrarios del usuario.

## 4. Redes y puertos

- Red **por instalación** para aislar clientes.
- Sin publicar puertos al host salvo lo imprescindible.
- Publicación preferente vía proxy/túnel ([`DECISIONS.md`](./DECISIONS.md#adr-010)).
- No exponer puertos de bases de datos de negocio al host.

## 5. Volúmenes y persistencia

- Volúmenes con nombre por instalación; nunca `bind` a rutas sensibles del host.
- Datos de negocio en **una base por cliente** (ADR-012).
- Sin montar `/var/run/docker.sock` en contenedores de aplicación.
- Política de backup definida por instalación ([`OPERATIONS.md`](./OPERATIONS.md)).

## 6. Compose de EVAS Admin (esqueleto propuesto)

```yaml
# ops/compose.yaml  (propuesta; sin servicio PostgreSQL)
services:
  api:
    build: ../backend
    env_file: [../.env]
    networks: [evas_admin_net]
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request;urllib.request.urlopen('http://localhost:8000/healthz')"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  web:
    build: ../frontend
    env_file: [../.env]
    networks: [evas_admin_net]
    depends_on: [api]
    restart: unless-stopped

  agent:
    build: ../agent
    env_file: [../.env]
    networks: [evas_admin_net]
    restart: unless-stopped
    # Modo simulated por defecto. En modo real: montar el socket Docker SOLO aquí,
    # con permisos mínimos y tras revisión de seguridad (ADR-007).

networks:
  evas_admin_net:
    driver: bridge
```

> Versiones de imagen/base fijas (no `latest`). Sin `privileged`.

## 7. Healthchecks

- Obligatorios en `api` y en cada servicio de instalación.
- Endpoint `healthz`/`readyz` en el backend ([`API_CONTRACTS.md`](./API_CONTRACTS.md)).
- El agente expone el estado de salud por instalación.

## 8. Logs

- `logging` con límite de tamaño y número de archivos (rotación).
- Formato estructurado; **saneado** (sin secretos).
- Retención definida en [`OPERATIONS.md`](./OPERATIONS.md).

## 9. Agente de Operaciones

- **Componente propio de este proyecto** (`agent/`), en su contenedor del
  Compose (ADR-007).
- Operaciones **tipadas** y permisos mínimos.
- No acepta imágenes, montajes, puertos ni privilegios arbitrarios.
- Acceso a Docker acotado a recursos etiquetados con `evas.managed_by`.
- Autenticación por token/mTLS y auditoría por operación.
- **Modos:** `simulated` (sin cambios reales; local/MVP) y `real` (autorización
  humana + revisión de seguridad).

## 10. Actualizaciones y rollback

- Sólo a versiones **aprobadas** registradas en el catálogo.
- Política de backup previa a la actualización ([`OPERATIONS.md`](./OPERATIONS.md)).
- Rollback documentado cuando sea posible.
- Verificación con healthchecks tras la operación.

## 11. Pendientes de confirmación

1. Estrategia de TLS y exposición vía Cloudflare Tunnel (ADR-010).
2. ¿Un contenedor por servicio o varios? [POR VERIFICAR]
3. Registro de imágenes (registry) privado y credenciales. [POR VERIFICAR]
4. Contrato exacto del canal backend⇄agente (mTLS vs token). [POR VERIFICAR]
