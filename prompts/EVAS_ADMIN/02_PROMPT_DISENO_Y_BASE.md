# PASO 2 | Diseño responsive y estructura base

Lee la documentación vigente en `docs/EVAS_ADMIN/`. Implementa únicamente el esqueleto de frontend y backend necesario para arrancar el proyecto.

Frontend:
- SvelteKit + TypeScript.
- Tailwind CSS y biblioteca de componentes compatible, escogida y documentada.
- Interfaz profesional HAPMED/EVAS, adaptable a móvil, tablet y escritorio.
- Navegación de escritorio y patrón de navegación móvil adecuado.
- Estados de carga, vacío, error, éxito y falta de permisos.
- Formularios accesibles, foco visible, contraste suficiente y uso por teclado.
- Componentes reutilizables para tablas, filtros, paginación, formularios, diálogos y estados.
- No depender solo del color para indicar estados.
- No presentar datos ficticios como reales.

Backend:
- FastAPI con estructura modular.
- Configuración centralizada mediante variables de entorno.
- Esquema inicial de SQLAlchemy y configuración de Alembic, sin ejecutar migraciones contra infraestructura real.
- Endpoints de salud/readiness sin filtrar secretos.
- Documentación OpenAPI.
- `.env.example` con nombres de variables y valores ficticios no sensibles.

No conectes todavía operaciones Docker reales ni modifiques PostgreSQL existente. Si hace falta probar la base, usa un mock o una configuración local explícitamente separada. Actualiza `UX_DESIGN_SYSTEM.md`, `ARCHITECTURE.md` y el README.
Ejecuta lint, comprobación de tipos y pruebas disponibles; reporta resultados reales.
