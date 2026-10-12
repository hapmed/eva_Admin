# REQUISITOS_EVA.md — Contrato para que EVAS Admin administre y despliegue una EVA

Una **EVA** es una app de negocio de HAPMED. Para que **EVAS Admin** pueda
instalarla por cliente, darle dominio y base de datos, monitorizarla y
actualizarla, la EVA debe cumplir este contrato.

## 1. Empaquetado

- Se entrega como **imagen Docker** (Linux), **versionada** (semver, p. ej.
  `1.4.2`). **Nunca** `latest` en producción.
- Se publica en un registro (p. ej. GHCR: `ghcr.io/hapmed/eva-<code>`), con
  etiquetas por versión y por commit (`sha-<commit>`).
- Build reproducible y determinista; **sin secretos** en la imagen.
- Proceso **no root**, sin `privileged`, sin montar `/var/run/docker.sock`.

## 2. Manifiesto (`eva.yaml`)

Describe la EVA a EVAS Admin. Ver [`MANIFEST_EJEMPLO.yaml`](./MANIFEST_EJEMPLO.yaml).
Campos:

| Campo | Descripción |
|-------|-------------|
| `code` | Identificador **estable** (minúsculas, sin espacios). No cambia nunca. |
| `name`, `description` | Nombre y descripción para el catálogo. |
| `image` | Repositorio de la imagen (sin tag). |
| `versions[]` | Versiones y estado (`approved`/`deprecated`/`blocked`). **Solo `approved` se despliega.** |
| `port` | Puerto HTTP interno único. |
| `healthcheck` | Ruta de salud (por defecto `/healthz`). |
| `config_schema` | Esquema de configuración permitida (subconjunto JSON Schema: `properties` con `type` y `required`). |
| `env[]` | Nombres de variables de entorno que el runtime inyecta. |
| `secrets[]` | Referencias a secretos (`key`, `provider`). **Nunca el valor.** |
| `migrate` | Comando de migración de base de datos (opcional). |
| `resources` | Límites de CPU/memoria (propuestos). |

## 3. Contrato del contenedor

- Escucha HTTP en **un único puerto** (`PORT`, por defecto `8000`), bind
  `0.0.0.0`. **No** publica puertos al host (los expone el proxy/túnel).
- **Healthcheck:** `GET <healthcheck>` devuelve `200` cuando está **listo**
  (no solo vivo). Es lo que usa EVAS Admin para confirmar cada despliegue.
- **Logs a stdout/stderr**, estructurados y **saneados** (sin secretos).
- **Apagado ordenado** ante `SIGTERM`.
- Configuración y secretos **solo por variables de entorno** (nunca en la imagen).

## 4. Labels de contenedor (obligatorias)

```yaml
labels:
  evas.managed_by: evas-admin
  evas.eva_code: <code>
  evas.version: <versión>
  # las añade EVAS Admin al desplegar:
  #   evas.installation_id, evas.client_ref
```

Permiten que el agente identifique los recursos **sin aceptar nombres
arbitrarios** del usuario.

## 5. Configuración y secretos

- La EVA declara `config_schema`; EVAS Admin **valida** la configuración del
  cliente contra ese esquema (solo claves declaradas y tipos correctos).
- Cada valor configurable llega como **variable de entorno**. Convención de
  variables de plataforma:

| Variable | Contenido |
|----------|-----------|
| `EVAS_EVA_CODE` | Código de la EVA. |
| `EVAS_INSTALLATION_ID` | Id de la instalación (cliente+EVA). |
| `EVAS_CLIENT_REF` | Referencia del cliente. |
| `EVAS_VERSION` | Versión desplegada. |
| `DATABASE_URL` | Conexión a **su** base de datos PostgreSQL. |
| `PORT` | Puerto HTTP. |

- Los **secretos** se referencian (`secret_reference`) y se inyectan como
  variables con un nombre declarado (p. ej. `DB_PASSWORD`). Nunca se guardan ni
  se muestran en claro en EVAS Admin.

## 6. Base de datos

- **Una base PostgreSQL por cliente** (ADR-012). La EVA **no** comparte base con
  otras EVAs ni clientes.
- La EVA aplica sus **migraciones** al arrancar o mediante el comando `migrate`.
  Debe ser idempotente.
- Sus datos deben poder ser **respaldados/restaurados** (comando/servicio
  conocido o base PostgreSQL estándar) — el agente solicita `request_backup` /
  `request_restore`.
- No imprimir cadenas de conexión ni credenciales.

## 7. Dominio

- La EVA se publica en un **dominio/subdominio registrado en EVAS Admin**
  (p. ej. `cotizaciones.cliente-x.hapmed.qzz.io`).
- EVAS Admin gestiona el conflicto de dominios; la EVA no necesita configurar
  TLS (lo termina el túnel/proxy).

## 8. Versiones y actualizaciones

- **Solo** se despliegan versiones `approved`. El flujo de actualización:
  validar versión → registrar solicitud → backup → desplegar → healthchecks →
  registrar resultado. Debe existir **rollback** a la versión anterior.
- La EVA debe ser correcta ante **cambio de versión** por cambio de imagen
  (sin pasos manuales) y exponer su versión en `GET /healthz` o `/version`.

## 9. Operaciones del agente (lo que EVAS Admin le pedirá)

Operaciones **tipadas**, sin parámetros arbitrarios:

| Operación | Efecto esperado en la EVA |
|-----------|---------------------------|
| `deploy_installation` | Primer despliegue (crear contenedores, migrar, quedar healthy). |
| `upgrade_installation` | Cambiar a la versión objetivo y quedar healthy. |
| `restart_service` | Reiniciar un servicio concreto. |
| `health_check` | Devolver estado/healthcheck. |
| `request_backup` | Generar copia de su base de datos. |
| `request_restore` | Restaurar desde una copia. |

En el MVP de la plataforma el agente opera en modo **simulado** (no cambia nada
real); cuando se habilite el modo `real`, la EVA debe funcionar con las reglas de
arriba.

## 10. Observabilidad

- `GET /healthz` (salud) y, opcional, `GET /readyz` (preparada).
- Logs a stdout **saneados**; tamaño/retención los gestiona la plataforma.
- Métricas (CPU/RAM) opcionales; si se exponen, formato estándar.

## 11. Seguridad

- Sin secretos en imagen, repositorio ni logs.
- Dependencias e imágenes con **versión fija**.
- Validación estricta de entradas; errores sin detalles internos.
- Sin shell arbitrario ni endpoints que ejecuten comandos del usuario.
- Operaciones destructivas con confirmación/permisos (del lado de EVAS Admin).

## 12. Checklist de aceptación (para que EVAS Admin la administre)

- [ ] Imagen Docker versionada, no root, sin secretos, publicada en registro.
- [ ] `eva.yaml` con `code`, `image`, `versions`, `port`, `healthcheck`,
  `config_schema`, `env`, `secrets`, `migrate`.
- [ ] Escucha en `PORT`/`0.0.0.0` y expone `healthcheck` que devuelve 200.
- [ ] Configuración y secretos por variables de entorno.
- [ ] Base de datos PostgreSQL propia por cliente + migraciones idempotentes.
- [ ] Logs saneados a stdout; apagado ordenado.
- [ ] Labels `evas.managed_by`, `evas.eva_code`, `evas.version`.
- [ ] Diseño equivalente a EVAS Admin (ver [`DISENO_EVA.md`](./DISENO_EVA.md)).
- [ ] Versionado semver con rollback.
