# MANUAL — EVAS Admin (uso básico)

Guía sencilla de uso. Para detalles técnicos, ver [`docs/EVAS_ADMIN/`](docs/EVAS_ADMIN/).

---

## 1. Entrar

- **URL:** https://evas.hapmed.qzz.io
- Te pide correo y contraseña. (La primera vez verás solo el login; el resto aparece tras entrar.)
- **Dónde están las credenciales:** en el servidor HomeLab, archivo `/opt/apps/eva_admin/.admin-credentials`.
  Por defecto: `h@hapmed.qzz.io`.
- **Passkeys (entrar sin contraseña):** en el login pulsa **«Entrar con passkey»** o, si tu
  dispositivo tiene una guardada, el navegador te la sugiere al escribir el correo.

> Si entras por primera vez, ve a **Cuenta → Añadir passkey** para no volver a usar contraseña.

---

## 2. Qué hay en el menú

| Sección | Para qué sirve |
|---|---|
| **Dashboard** | Resumen: alertas, **estado del servidor** (CPU, RAM, disco, red) y avisos. |
| **Clientes** | Empresas (cada empresa es un cliente). |
| **Usuarios internos** | Cuentas del equipo HAPMED y sus roles. |
| **Catálogo EVA** | Las aplicaciones EVA y sus versiones. |
| **Suscripciones** | Planes y contratos (mensual/anual), tiempo transcurrido y vencimientos. |
| **Instalaciones** | Cada EVA montada para un cliente (versión, dominio, estado). |
| **Dominios** | Dominios/subdominios asignados. |
| **Bases de datos** | Metadatos (nombre, nodo, última copia). Nunca muestra contraseñas. |
| **Monitoreo** | Estado, salud, logs y métricas de cada instalación. |
| **Alertas** | Avisos abiertos (vencimientos, salud, backups). |
| **Cuenta** | Cambiar contraseña y gestionar passkeys. |

---

## 3. Ejemplos paso a paso

### 3.1 Crear un cliente
1. **Clientes → “Nuevo cliente”**.
2. Rellena *Nombre comercial*, *Razón social* e **Índice de cliente (RFC)** → **Crear**.
3. Para modificar datos: **Editar** en la fila y **Guardar cambios**.
4. Para suspender o archivar: botones **Suspender** / **Archivar** en la fila.

### 3.2 Registrar una EVA y su versión
1. **Catálogo EVA → “Nueva EVA”**: `Código` (ej. `cotizaciones`), `Nombre` → **Crear**.
2. En la fila, **“Añadir versión”**: `1.0.0`, estado **Aprobada** → **Añadir**.
   > Solo las versiones **aprobadas** se pueden instalar.

### 3.3 Crear un plan
1. **Suscripciones → “Nuevo plan”**.
2. `Código` (ej. `mensual`), `Nombre`, `Periodo` (mensual/anual), `Precio` → **Crear**.

### 3.4 Contratar (suscripción)
1. **Suscripciones → “Nueva suscripción”**.
2. Elige **Cliente** y **Plan** → **Crear**.
3. En la tabla puedes **Renovar** o **Cancelar**. La fecha de vencimiento se calcula sola.

### 3.5 Montar una instalación (aprovisiona de verdad)
1. **Instalaciones → “Nueva instalación”**: Cliente, EVA, Versión y **Dominio principal** → **Crear**.
2. Al crearla, la plataforma **crea automáticamente**:
   - una **base de datos** PostgreSQL propia del cliente;
   - el **contenedor** Docker de la EVA (publicado en `127.0.0.1`, accesible por el túnel);
   - el **DNS + ruta del túnel** (`https://<dominio>`) para el dominio indicado.
3. La instalación queda **activa**; con **Actualizar** subes de versión y en **Monitoreo → Detalle**
   ves logs y métricas.
4. Para eliminarla: **Instalaciones → Eliminar**, escribe `ELIMINAR` y confirma. Se borran el
   contenedor, la base de datos, el dominio y los registros; **el cliente se conserva**.

> El **catálogo EVA** debe tener `Imagen Docker`, `Puerto interno` y `Ruta de salud`
> (se definen al crear la EVA).

### 3.6 Renovar / cancelar una suscripción
1. **Suscripciones**: en la fila pulsa **Renovar** o **Cancelar**.

### 3.7 Bases de datos, copias y restauración
1. **Bases de datos**: la instalación ya crea su base; aquí puedes registrar metadatos si hace falta.
2. **Backup**: botón **Backup** en la fila → hace `pg_dump` real y guarda la copia en el servidor.
3. **Copias**: botón **Copias** → lista las copias (fecha, estado, tamaño).
4. **Restaurar**: en “Copias”, escribe el **nombre de la base** para confirmar y restaura.
   - Antes de restaurar se hace **una copia de seguridad previa** automáticamente.
   - Restaurar es **destructivo**: requiere permiso `backups:restore`, confirmación y auditoría.

### 3.8 Ver estado de una instalación
1. **Monitoreo**: lista de instalaciones.
   - **Comprobar salud** → lanza un chequeo.
   - **Detalle** → muestra servicios, **logs** y **métricas** (real, del contenedor).

### 3.9 Alertas
- **Dashboard** y **Alertas** muestran los avisos. Puedes **Reconocer** o **Resolver** cada alerta.
- La **campana** (arriba a la derecha) muestra el número de alertas abiertas.

### 3.10 Tu cuenta
- **Cuenta → Cambiar contraseña**: pide la actual y la nueva.
- **Cuenta → Añadir passkey**: crea una passkey; se le pone un **nombre de animal** (ej. «Brave Badger») que verás junto a tu correo.

---

## 4. Estado del servidor (Dashboard)

En el **Dashboard** verás tres anillos con el **estado actual** del servidor HomeLab:
- **CPU** (%), **RAM** (%), **Disco** (%).
- Debajo: carga (1/5/15), tiempo encendido y **tráfico de red** (entrada/salida por segundo).

Estos datos los lee el **agente** desde el host (monta `/proc` y `/` en solo lectura).
Si aparece «modo simulado», el agente no está en modo real.

---

## 5. Notificaciones por email (SMTP) — dónde se configura

Se configuran en el **servidor HomeLab**, en el archivo:

```
/opt/apps/eva_admin/.env
```

Añade/edita el bloque `EVAS_SMTP_*` (ejemplo):

```dotenv
EVAS_SMTP_ENABLED=true
EVAS_SMTP_HOST=smtp.tuproveedor.com
EVAS_SMTP_PORT=587
EVAS_SMTP_USER=evas-admin@tudominio.com
EVAS_SMTP_PASSWORD=tu-contraseña-smtp
EVAS_SMTP_FROM=evas-admin@tudominio.com
EVAS_SMTP_TO=["operaciones@tudominio.com","jefe@tudominio.com"]
EVAS_SMTP_STARTTLS=true
EVAS_SMTP_SSL=false
```

- `EVAS_SMTP_TO` es una **lista JSON** de destinatarios.
- Si tu proveedor usa **SSL directo** (puerto 465): `EVAS_SMTP_SSL=true` y `EVAS_SMTP_PORT=465`.

**Probar el envío ahora** (sin esperar):

```bash
cd /opt/apps/eva_admin
docker compose -f ops/compose.prod.yaml run --rm --no-deps api python -m app.cli notify-alerts
# -> "alertas notificadas: N"
```

**Automático:** ya hay un timer que envía el resumen **cada día a las 08:00**
(`hapmed-alerts.timer`). Comprueba con:

```bash
systemctl list-timers 'hapmed-*' --no-pager
```

### 5.1 Aprovisionamiento (base de datos + contenedores + DNS)

También en `/opt/apps/eva_admin/.env`, bloque de aprovisionamiento real:

```dotenv
EVAS_PROVISION_ENABLED=true
EVAS_PROVISION_DB_HOST=postgres
EVAS_PROVISION_DB_ADMIN_USER=<usuario_admin_postgres>
EVAS_PROVISION_DB_ADMIN_PASSWORD=<clave_admin_postgres>
EVAS_PROVISION_DB_ADMIN_DB=postgres
EVAS_PORT_RANGE_START=9100
EVAS_PORT_RANGE_END=9199
EVAS_EVA_NETWORK=apps-net

# Cloudflare (publicar dominios de clientes)
EVAS_PUBLIC_DOMAIN_SUFFIX=hapmed.qzz.io
EVAS_CLOUDFLARE_API_TOKEN=<token_con_Tunnel_y_DNS_Edit>
EVAS_CLOUDFLARE_ACCOUNT_ID=<account_id>
EVAS_CLOUDFLARE_ZONE_ID=<zone_id>
EVAS_CLOUDFLARE_TUNNEL_ID=<tunnel_id>
```

Con esto, **crear una instalación crea la BD, el contenedor y el DNS/túnel** solos.

---

## 6. Cosas útiles del servidor (para mantenimiento)

Ejecutar como `hapmed` (`su -`) en `192.168.0.14`:

```bash
# Ver contenedores
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Estado / actualizar EVAS Admin
cd /opt/apps/eva_admin
docker compose -f ops/compose.prod.yaml ps
docker compose -f ops/compose.prod.yaml pull && docker compose -f ops/compose.prod.yaml up -d

# Backups locales (se hacen solos a las 03:00)
ls -lh /opt/apps/backups/dumps

# Actualización automática: al hacer push a GitHub, el servidor se
# actualiza solo en ≤3 min (timer evas-deploy.timer).
```

---

## 7. Qué hace el “modo real” del agente

- **Funciona real:** comprobar **salud**, **reiniciar** un servicio, **logs** y **métricas**.
- **Todavía no real:** *desplegar*, *actualizar versión*, *backup/restore* desde el panel
  (responden con un aviso claro). Se implementarán con el “manifiesto de despliegue”.

---

## 8. Seguridad (importante)

- El archivo `contras.txt` (contraseñas) es **privado**: no lo subas a Git ni lo compartas.
- El panel exige sesión para todo; sin login solo se ve la pantalla de acceso.
- Para operaciones destructivas, el sistema pide confirmación.
