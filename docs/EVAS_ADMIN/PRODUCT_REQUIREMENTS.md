# PRODUCT_REQUIREMENTS.md — Requisitos de producto de EVAS Admin

**Estado:** Borrador inicial para revisión.
**Documentos relacionados:** [`README.md`](./README.md),
[`DATA_MODEL.md`](./DATA_MODEL.md), [`API_CONTRACTS.md`](./API_CONTRACTS.md).

## 1. Objetivo

Centralizar la administración comercial y operativa de las aplicaciones EVA que
HAPMED entrega a sus clientes: quién es el cliente, qué contrató, qué tiene
instalado, dónde, con qué dominio y base de datos, en qué estado está y qué
operaciones se le han aplicado.

## 2. Roles y actores

| Rol | Ámbito | Descripción |
|-----|--------|-------------|
| **Superadministrador** | HAPMED | Control total, incluida gestión de usuarios internos y roles. |
| **Operaciones** | HAPMED | Instalaciones, monitoreo, actualizaciones, backups. |
| **Atención al cliente** | HAPMED | Consulta de clientes, suscripciones y estado; sin operaciones destructivas. |
| **Solo lectura** | HAPMED | Consulta sin modificación. |
| **Usuario de cliente** | Cliente | Acceso limitado a su propia empresa (roles separados). [POR VERIFICAR: alcance exacto] |

## 3. Módulos funcionales y criterios de aceptación

### 3.1 Dashboard

- Resumen de clientes activos, suscripciones por vencer, instalaciones con
  problemas de salud y alertas abiertas.
- **Criterio:** los datos mostrados son reales (nunca ficticios presentados como
  reales); si no hay datos, se muestra estado vacío explícito.

### 3.2 Usuarios internos HAPMED, roles y permisos

- Alta, edición, desactivación/reactivación de usuarios internos.
- Asignación de roles; autorización por permisos.
- **Criterios:** no se permite autoelevación de privilegios; contraseñas con hash
  seguro; acciones auditadas.

### 3.3 Clientes/empresas y usuarios de cliente

- Alta, consulta, edición, suspensión y **archivo lógico** (no borrado físico).
- Varios usuarios por cliente.
- **Criterio:** aislamiento estricto entre empresas en cada endpoint y consulta;
  toda modificación se audita.

### 3.4 Catálogo de aplicaciones EVA

- Nombre, identificador estable, descripción, estado, versiones admitidas y
  requisitos de despliegue.
- **Criterio:** no se aceptan imágenes Docker ni parámetros arbitrarios del
  usuario; sólo EVA y versiones registradas.

### 3.5 Suscripciones, planes y vencimientos

- Planes mensuales y anuales.
- Fechas de inicio, renovación y vencimiento; historial de cambios.
- Estados de dominio con transiciones válidas.
- Alertas configurables previas al vencimiento y para vencidas.
- **Criterios:** fechas en UTC mostradas en zona configurada; no se suspendan ni
  borran instalaciones automáticamente sin política aprobada; sin pagos reales en
  esta fase.

### 3.6 Instalaciones/instancias por cliente

- Crear y consultar instalaciones; asociar cliente, EVA, suscripción y nodo.
- Estado, versión deseada e instalada, resultado de la última actualización.
- **Criterio:** cada entidad es independiente (cliente ≠ suscripción ≠ EVA ≠
  instalación).

### 3.7 Dominios y subdominios

- Registro de dominios por instalación; comprobación de conflictos.
- **Criterio:** no se permite un dominio duplicado activo sin resolución
  explícita.

### 3.8 Bases de datos asignadas a instalaciones

- Metadatos: motor, nombre lógico, host/nodo, estado, última copia de seguridad.
- **Criterio:** nunca se muestran credenciales guardadas; la base de EVAS Admin
  está separada de las bases de negocio de clientes.

### 3.9 Monitoreo de Docker, healthchecks, logs y métricas

- Estado de aplicación y contenedores, healthcheck, CPU/RAM si están disponibles.
- Historial de eventos y **logs saneados** (sin secretos), con tamaño/retención
  limitados.
- **Criterio:** operaciones Docker simuladas o vía agente autorizado; sin shell
  arbitrario.

### 3.10 Actualizaciones controladas

- Actualizar a una versión aprobada, con validación, backup según política,
  healthchecks y registro de resultado.
- **Criterio:** toda actualización queda auditada (actor, instalación, operación,
  fecha, resultado); rollback documentado cuando sea posible.

### 3.11 Auditoría, alertas y respaldo/restauración

- Registro de auditoría de operaciones administrativas críticas.
- Alertas configurables y notificaciones (canal [POR VERIFICAR]).
- Flujo específico para solicitar backup/restauración.
- **Criterio:** sin secretos en los registros; operaciones destructivas con
  permisos específicos, confirmación y auditoría.

## 4. Requisitos no funcionales

| ID | Requisito |
|----|-----------|
| RNF-01 | Interfaz responsive para móvil, tablet y PC. |
| RNF-02 | Accesibilidad: foco visible, contraste suficiente, uso por teclado. |
| RNF-03 | Estados de carga, vacío, error, éxito y falta de permisos en toda vista. |
| RNF-04 | No depender sólo del color para indicar estados. |
| RNF-05 | Fechas en UTC almacenadas; mostradas en zona configurada. |
| RNF-06 | Rendimiento: respuesta de API < 1 s en operaciones de lectura típicas. [PROPUESTA] |
| RNF-07 | Trazabilidad: toda operación crítica auditada. |
| RNF-08 | Seguridad conforme a [`SECURITY.md`](./SECURITY.md). |

## 5. Fuera de alcance (MVP)

- Pagos reales y facturación.
- Aprovisionamiento real sobre Docker sin autorización.
- Migraciones contra el PostgreSQL productivo existente.
- PWA como requisito bloqueante.
- Autoescalado, HA multi-región.

## 6. Métricas de éxito (propuestas)

- Reducción del tiempo de alta de un cliente/instalación.
- Visibilidad en un solo panel del estado de todas las instalaciones.
- Cero acciones destructivas sin auditoría.
- Cero secretos en repositorio, logs o documentación.

## 7. Preguntas abiertas

1. ¿Los usuarios de cliente acceden a EVAS Admin o este panel es sólo interno?
2. ¿Qué canal de notificación de alertas se usará (email, Slack, webhook)?
3. ¿Qué política de suspensión automática por impago, si alguna, se aprueba?
4. ¿Qué EVA concretas existen y qué requisitos de despliegue tienen?
