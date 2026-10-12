# POSTGRES_EXISTING_INSTANCE.md — Instancia PostgreSQL preexistente

**Estado:** Requisitos y procedimiento. Información real **[POR VERIFICAR]**.
**Documentos relacionados:** [`ARCHITECTURE.md`](./ARCHITECTURE.md),
[`DOCKER_STANDARD.md`](./DOCKER_STANDARD.md), [`SECURITY.md`](./SECURITY.md).

## 1. Regla inquebrantable

> Ya existe **un contenedor Docker con PostgreSQL**. EVAS Admin:
> - **NO** crea otro contenedor PostgreSQL.
> - **NO** reinicia, actualiza, detiene ni elimina el contenedor existente.
> - **NO** cambia su configuración, redes, volúmenes, roles, contraseñas ni
>   versión.
> - **NO** ejecuta comandos destructivos ni migraciones productivas.
> - **NO** crea bases ni usuarios hasta confirmar qué contiene, quién lo usa y
>   qué permisos hay disponibles.

EVAS Admin **usa** esta instancia para su **base administrativa**, que es
**independiente** de las bases de negocio de clientes.

## 2. Objetivo de la inspección

Reunir, sin imprimir secretos, la información mínima para decidir cómo conectar
la base administrativa:

- Nombre lógico del contenedor y estado.
- Imagen y versión de PostgreSQL.
- Redes a las que está conectado.
- Volúmenes y persistencia.
- Bases de datos y roles existentes (sin contraseñas).
- Aplicaciones que ya consumen esta instancia.
- Capacidad del servidor y permisos disponibles para crear la base administrativa.

## 3. Procedimiento de inspección segura (READ-ONLY)

> Ejecutar **sólo** con autorización humana y en horario controlado. Todos los
> comandos siguientes son de **sólo lectura**. Nunca imprimir el bloque `Env` de
> `docker inspect` (contiene contraseñas) ni volcar credenciales.

```bash
# 3.1 Identificar el contenedor y su imagen/estado (sin secretos)
docker ps --filter "ancestor=postgres" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 3.2 Ver redes y volúmenes asociados (sin secretos)
docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' <container>
docker inspect -f '{{json .Mounts}}' <container>

# 3.3 NUNCA ejecutar sin filtrar: docker inspect <container>   (expone Env con contraseñas)

# 3.4 Listar bases y roles (requiere credenciales de administrador; READ-ONLY)
#     Conectar como un usuario administrador ya existente y listar.
# docker exec -it <container> psql -U <admin_user> -c "\l"
# docker exec -it <container> psql -U <admin_user> -c "\du"
```

Reglas durante la inspección:

- No ejecutar `ALTER`, `DROP`, `CREATE`, `UPDATE`, `DELETE`, `VACUUM FULL`,
  `docker restart/stop/rm/update`, ni cambios de versión.
- No imprimir `POSTGRES_PASSWORD`, `PGPASSWORD` ni cadenas de conexión.
- Registrar sólo metadatos (nombres, versiones, estados).

## 4. Información a recolectar (plantilla)

| Dato | Valor | Estado |
|------|-------|--------|
| Nombre del contenedor | `[POR VERIFICAR]` | |
| Imagen / versión PostgreSQL | `[POR VERIFICAR]` | |
| Estado (`Up`/`healthy`) | `[POR VERIFICAR]` | |
| Redes | `[POR VERIFICAR]` | |
| Volúmenes / persistencia | `[POR VERIFICAR]` | |
| Bases existentes | `[POR VERIFICAR]` | |
| Roles existentes | `[POR VERIFICAR]` | |
| Aplicaciones consumidoras | `[POR VERIFICAR]` | |
| Capacidad del host (CPU/RAM/disco) | `[POR VERIFICAR]` | |
| ¿Se puede crear la base administrativa? | `[POR VERIFICAR]` | |
| ¿Qué rol/credencial usará EVAS Admin? | `[POR VERIFICAR]` | |

## 5. Separación de bases

| Base | Propósito | Contenido |
|------|-----------|-----------|
| `evas_admin` (nombre propuesto) | Base administrativa de EVAS | Clientes, suscripciones, EVA, instalaciones, auditoría… |
| Bases de negocio de clientes | Datos de negocio de cada cliente | Datos operativos de cada cliente |

> [POR VERIFICAR] Si la base administrativa se crea en esta misma instancia o en
> otra, y con qué rol dedicado. **No** se crea ninguna base hasta confirmar
> permisos y capacidad.

## 6. Conexión mediante variables de entorno

Nombres propuestos (valores **ficticios**; los reales nunca en Git):

```dotenv
# .env.example  (valores de ejemplo, NO reales)
EVAS_DB_HOST=postgres.example.internal
EVAS_DB_PORT=5432
EVAS_DB_NAME=evas_admin
EVAS_DB_USER=evas_admin_app
EVAS_DB_PASSWORD=change-me-in-env
EVAS_DB_SSLMODE=require
```

Reglas:

- Credenciales sólo por entorno o gestor de secretos ([`SECURITY.md`](./SECURITY.md)).
- Rol de aplicación con **mínimo privilegio** (no superusuario).
- Sin cadenas de conexión reales en el repositorio ni en logs.

## 7. Preguntas concretas a confirmar

1. ¿Cuál es el nombre del contenedor y su versión de PostgreSQL?
2. ¿Qué bases y roles existen y quién los consume?
3. ¿Hay margen de CPU/RAM/disco para una base administrativa más?
4. ¿Se permite crear una base `evas_admin` y un rol de aplicación dedicado?
5. ¿Debe usarse un `schema` dentro de una base existente en lugar de una base nueva?
6. ¿Requiere `sslmode`/TLS interno?
7. ¿Existe política de backup ya aplicada a esta instancia?
8. ¿Quién autoriza la creación de la base administrativa y cuándo?

## 8. Marcadores de autorización

Ninguna acción de escritura sobre la instancia se ejecuta sin:

- [ ] Confirmación del contenido y uso actual de la instancia.
- [ ] Autorización explícita de HAPMED para crear la base/rol administrativos.
- [ ] Backup previo de la instancia (si aplica).
- [ ] Registro de la operación (auditoría).
