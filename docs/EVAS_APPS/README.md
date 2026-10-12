# EVAS Apps — Kit para construir una EVA compatible con EVAS Admin

Esta carpeta es **material de entrega**: cópiala/sela como contexto para otro
agente que vaya a desarrollar una **EVA** (aplicación de negocio de HAPMED) que
debe poder ser **administrada y desplegada por EVAS Admin**.

| Documento | Para qué sirve |
|-----------|----------------|
| [`COMO_FUNCIONA_EVAS_ADMIN.md`](./COMO_FUNCIONA_EVAS_ADMIN.md) | Explicación sencilla («como peras y manzanas») de qué es y cómo funciona EVAS Admin. |
| [`DISENO_EVA.md`](./DISENO_EVA.md) | El **diseño visual** a replicar (tokens de marca, componentes, tema claro/oscuro, accesibilidad). |
| [`REQUISITOS_EVA.md`](./REQUISITOS_EVA.md) | **Contrato/requisitos** que la EVA debe cumplir para que EVAS Admin la administre y despliegue. |
| [`MANIFEST_EJEMPLO.yaml`](./MANIFEST_EJEMPLO.yaml) | Ejemplo del **manifiesto** (`eva.yaml`) que describe la EVA a EVAS Admin. |
| [`PROMPT_AGENTE_EVA.md`](./PROMPT_AGENTE_EVA.md) | Prompt listo para pegar al **otro agente** y empezar el desarrollo. |

> La fuente de verdad de la plataforma está en [`../EVAS_ADMIN/`](../EVAS_ADMIN/).
> Este kit es un resumen orientado a quien construye una EVA.

## Orden recomendado de lectura

1. `COMO_FUNCIONA_EVAS_ADMIN.md` — entender el contexto.
2. `REQUISITOS_EVA.md` — lo que hay que cumplir (el contrato).
3. `DISENO_EVA.md` — cómo debe verse.
4. `MANIFEST_EJEMPLO.yaml` — el contrato en formato máquina.
5. `PROMPT_AGENTE_EVA.md` — para lanzar al agente.
