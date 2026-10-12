# DISENO_EVA.md — Diseño de una EVA (mismo estilo que EVAS Admin)

Objetivo: que una EVA se vea **idéntica en lenguaje visual** a EVAS Admin
(Apple HIG + marca HAPMED), de modo que el conjunto parezca un solo producto.

**Stack recomendado (el mismo de EVAS Admin):** SvelteKit 3 + TypeScript +
Tailwind CSS v4 (`@tailwindcss/vite`), iconos `@lucide/svelte`, adaptador
`@sveltejs/adapter-node`. Se puede usar otra tecnología, pero **replicando los
tokens y componentes** de abajo.

## 1. Tokens (valores exactos de marca HAPMED)

```css
/* src/app.css */
@import 'tailwindcss';
@custom-variant dark (&:where(.dark, .dark *));

@theme {
	--color-bg: #fbfbfd;
	--color-surface: #ffffff;
	--color-surface-2: #f2f2f7;
	--color-ink: #1d1d1f;
	--color-ink-2: #6e6e73;
	--color-ink-3: #8a8a8f;
	--color-line: rgba(0, 0, 0, 0.08);
	--color-accent: #2e6bff;
	--color-accent-2: #00c2b8;
	--color-success: #34c759;
	--color-warning: #ff9500;
	--color-danger: #ff3b30;

	--radius-brand: 16px;
	--radius-brand-lg: 24px;

	--font-sans: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto,
		Helvetica, Arial, sans-serif;
	--ease-brand: cubic-bezier(0.22, 0.61, 0.36, 1);
}

@layer base {
	.dark {
		--color-bg: #0b0c0e;
		--color-surface: #141518;
		--color-surface-2: #1b2340;
		--color-ink: #f5f5f7;
		--color-ink-2: #a7abb3;
		--color-ink-3: #6e737c;
		--color-line: rgba(255, 255, 255, 0.1);
		--color-accent: #5b8cff;
		--color-accent-2: #2fd6cd;
	}
	body {
		background-color: var(--color-bg);
		color: var(--color-ink);
		font-family: var(--font-sans);
		-webkit-font-smoothing: antialiased;
	}
	*:focus-visible {
		outline: 2px solid var(--color-accent);
		outline-offset: 2px;
	}
}
```

- **Tema claro y oscuro** (clase `.dark` en `<html>`; guardar preferencia en
  `localStorage('evas-theme')` y respetar `prefers-color-scheme` al entrar).
- **Gradiente firma:** `linear-gradient(135deg,#2e6bff,#00c2b8)`.
- Tamaños de texto recomendados: `28px` títulos de página (semibold), `17px`
  cuerpo, `14–15px` secundario, `12–13px` metadatos.
- **Radios**: `16px` (controles/tarjetas), `24px` (contenedores grandes).
- Controles con altura mínima **44px** (accesibilidad táctil).

## 2. Componentes a replicar

| Componente | Uso |
|-----------|-----|
| `Button` | variantes `primary` (acento), `secondary`, `ghost`, `danger`; `disabled`. |
| `PageHeader` | título + subtítulo + zona de acciones. |
| `DataTable` | tabla con encabezados, estados vacíos y columna de acciones. |
| `EmptyState` | título + descripción + acción. |
| `StatusBadge` | estado con **color + icono + texto** (nunca solo color). |
| `Modal` | diálogos de formulario / confirmación (acciones destructivas). |
| `ThemeToggle` | conmutador claro/oscuro. |
| `NavList` | navegación agrupada (ver §4). |
| `Toast` / `InlineAlert` | avisos de éxito/error/aviso. |

Están en el repo de referencia en `frontend/src/lib/components/` — **se pueden
copiar tal cual** a la EVA (son Svelte 5, sin dependencias de EVAS Admin).

## 3. Estados obligatorios por vista

Cargando (skeleton) · Vacío (mensaje + acción) · Error (comprensible, con
reintento, sin detalles internos) · Éxito (aviso discreto) · Sin permisos.

> Regla: **no** mostrar datos ficticios como si fueran reales; usar «—» o estado
> vacío.

## 4. Navegación

- **Escritorio (≥1024px):** barra lateral fija a la izquierda con grupos
  (secciones) y el logo HAPMED arriba. Ancho ~264px.
- **Móvil/tablet:** cabecera con botón de menú que abre un **drawer**; contenido
  a ancho completo.
- **Cabecera:** a la derecha, correo del usuario y botón «Salir» (y el chip de
  passkey si aplica).
- Máximo **dos niveles** de jerarquía.

## 5. Marca

- Símbolo (mascota) y wordmark **HAPMED**; activos en [`../../brand/`](../../brand/).
- La marca **cede ante el contenido**: no repetir el logo; usarlo en la barra
  lateral, login y estados vacíos.
- Wordmark: `font-weight: 700`, `letter-spacing: 0.18em–0.22em`, color `--ink`.

## 6. Accesibilidad

- Contraste **WCAG AA** (≥4.5:1 en texto normal; ≥3:1 en grande/negrita).
- Foco visible; navegación por teclado; etiquetas en formularios.
- No depender del color; tamaños de control ≥44px.
- Respetar `prefers-reduced-motion`.

## 7. Cómo reutilizar del repo de referencia

1. Copiar `frontend/src/app.css` (tokens) y `frontend/src/lib/components/*`.
2. Copiar `frontend/src/lib/format.ts` y `frontend/src/lib/api/client.ts` como
   base del cliente HTTP.
3. Reutilizar la estructura de rutas: `+layout.svelte` (shell) + páginas por
   módulo con `PageHeader` + `DataTable`/`EmptyState`.

Ver también [`../EVAS_ADMIN/UX_DESIGN_SYSTEM.md`](../EVAS_ADMIN/UX_DESIGN_SYSTEM.md).
