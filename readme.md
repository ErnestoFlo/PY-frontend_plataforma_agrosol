# AGROSOL Frontend (Django + HTMX + Tailwind)

Frontend server-rendered para AGROSOL, construido sobre Django templates con componentes parciales reutilizables (`django-template-partials`), interacciones HTMX y sistema de diseño en Tailwind CSS.

## Objetivo del proyecto

- Entregar una UI rápida de mantener sin SPA framework.
- Reutilizar componentes visuales y funcionales en vistas/módulos.
- Resolver CRUDs con render parcial + swaps HTMX (sin recargas completas).
- Mantener soporte desktop/mobile desde el mismo backend.

## Stack y materiales usados

### Backend / Python

- Django 5.x
- `django-template-partials`
- `django-widget-tweaks`
- `django-crispy-forms` + `crispy-tailwind` (compatibilidad de forms)
- `requests` (consumo de API externa)
- `urllib3` (manejo de advertencias TLS en desarrollo)

### Frontend

- HTMX (incluido localmente en `client/static/js/htmx.min.js`)
- Tailwind CSS (source en `client/static/css/input.css`, build en `output.css`)
- Flatpickr (`client/static/js/flatpickr.js` + locale `es.js`)
- Swiper (`client/static/js/swiper-bundle.min.js`)
- JavaScript vanilla modular (`ui.js` + `modules/proveedores_ui.js`)

### Recursos del proyecto

- Íconos SVG sprite (`client/static/sprite.svg`)
- Tipografías locales (`client/static/fonts`)
- Templates parciales reutilizables (`client/templates/components`, `client/templates/partials`)

## Inicio rápido

### Requisitos

- Python 3.9+
- Dependencias de `requirements.txt`
- Tailwind CLI disponible (el repo usa `tailwindcss.exe`)

### Setup local

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

En otra terminal (watch CSS):

```bash
.\tailwindcss.exe -i ./client/static/css/input.css -o ./client/static/css/output.css --watch
```

App principal:

- [http://localhost:8000/agrosol/proveedores/](http://localhost:8000/agrosol/proveedores/)

## Estructura actual del repositorio

```text
frontend/                 # settings.py, urls.py, wsgi/asgi
client/
  forms.py                # formularios Django
  urls.py                 # rutas del app
  views.py                # controladores HTTP + fragment routing HTMX
  utils.py                # mapping API->UI (rows, menu, paginación)
  services/
    proveedores.py        # cliente API para módulo proveedores
  templates/
    base.html
    layouts/
      navigation.html
      landing_login.html
    proveedores/
      index_proveedores.html
      form.html
      confirm_delete.html
    components/           # botones, inputs, modals, popovers, sidebar, etc.
    partials/             # tablas, options list, etc.
  static/
    css/input.css
    css/output.css
    js/ui.js
    js/modules/proveedores_ui.js
```

## Arquitectura de render y flujo runtime

1. URL entra por `frontend/urls.py` y se delega a `client/urls.py`.
2. Vista en `client/views.py` consulta servicios (`client/services/proveedores.py`).
3. `client/utils.py` transforma payload API al contrato de tabla/cards.
4. Django renderiza template completo o fragmento `#partial` según contexto HTMX.
5. HTMX reemplaza contenedores (`hx-target` + `hx-swap`) sin recargar la página.
6. `client/static/js/ui.js` orquesta eventos globales (`data-action`, modales, popovers, tema, sidebar).

## Conceptos base (para quien no conoce partials + HTMX)

### 1) `django-template-partials`

- Un archivo puede exponer múltiples bloques reutilizables con `{% partialdef %}`.
- Se incluyen con sintaxis: `"ruta/archivo.html#nombre_partial"`.
- Esto permite retornar fragmentos específicos desde una vista, no solo páginas completas.

Ejemplo real: `client/templates/partials/tables.html`

- `#table` (tabla desktop completa)
- `#table_rows` (solo filas)
- `#table_mobile` (cards mobile)
- `#table_pagination` (paginador)

### 2) HTMX

- Acciones HTML con atributos `hx-*`.
- El servidor sigue devolviendo HTML; HTMX lo inserta donde corresponda.
- Se usa para CRUD de proveedores, paginación y carga de formularios/modales.

## Contratos importantes de datos

### Contrato de fila de tabla (`utils.build_table_rows`)

Cada fila incluye campos usados por templates/JS:

- `id`
- `cells`
- `prior_cols` (mobile)
- `id_col` (título de card mobile)
- `edit_url`
- `delete_url`
- `detail_url`
- `actions_id` (popover por fila)

### Contrato de paginación (`utils.get_paginated_table_data`)

- `rows`
- `total_pages`
- `current_page`
- `page_items` (con `ellipsis`)

## Tutorial de implementación (paso a paso)

### A) Implementar una modal HTMX

1. Agrega contenedor modal en la vista (normalmente desde `components/modals.html`).
2. Botón disparador con `data-action="openModal"` y `hx-get` al endpoint del form/confirm.
3. En `ui.js`, `openModal()` carga skeleton y luego hace `htmx.ajax` al `hx-get`.
4. El backend retorna un partial (ej. `proveedores/form.html#form`).
5. El submit del form usa `hx-post` y cierra modal en `hx-on::after-request`.

Archivos guía:

- `client/static/js/ui.js`
- `client/templates/proveedores/form.html`
- `client/templates/components/modals.html`

### B) Implementar tabla con desktop/mobile

1. Crea contenedor con `data-responsive-table="<modulo>"` y `data-source-url`.
2. Inicializa módulo JS (`ProveedoresUI.initResponsiveTable(...)`).
3. Define en vista respuesta por fragmento:
   - `fragment=table` -> `partials/tables.html#table`
   - `fragment=table_mobile` -> `partials/tables.html#table_mobile`
4. Asegura `table_id` para que paginación apunte a `#<table_id>-container`.

Archivos guía:

- `client/static/js/modules/proveedores_ui.js`
- `client/views.py` (`list_proveedores`)
- `client/templates/partials/tables.html`

### C) Implementar formulario create/edit reutilizable

1. Usa una sola vista para create/edit (con `id=None` o `id=<int>`).
2. En GET, renderiza `form` vacío o con `initial`.
3. En POST:
   - create: refresca contenedor completo
   - edit desktop: reemplaza solo fila editada
   - mobile: refresca cards
4. Mantén `hx-target/hx-swap` condicionados en template.

Archivos guía:

- `client/views.py` (`create_or_edit_proveedor`)
- `client/templates/proveedores/form.html`
- `client/forms.py`

### D) Implementar acciones de tabla (editar/eliminar/popover)

1. Incluye botón de acciones por fila (popover).
2. Edit -> abre modal con form.
3. Delete -> abre confirmación con `confirm_delete`.
4. POST delete:
   - desktop: retornar `HttpResponse('')` para remover fila (`outerHTML`)
   - mobile: retornar listado mobile actualizado.

Archivos guía:

- `client/templates/partials/tables.html`
- `client/templates/components/popovers.html`
- `client/views.py` (`confirm_delete`, `delete_proveedor`)

### E) Agregar un nuevo módulo CRUD reutilizando la base

Checklist:

1. Añadir entrada en `MODELS_CONFIG` de `client/utils.py`.
2. Crear servicio API en `client/services/`.
3. Crear rutas en `client/urls.py`.
4. Crear vistas (list/create-edit/delete/confirm).
5. Reusar `partials/tables.html` + `components/*`.
6. Crear `templates/<modulo>/index_*.html` y `form.html`.
7. Registrar opción de menú en `MENU_SIDEBAR_ITEMS_CONFIG` y `MENU_MOBILEBAR_ITEMS_CONFIG`.

## Sistema de diseño (Tailwind)

- Fuente de verdad: `client/static/css/input.css`.
- Tokens de color/espaciado/radios/sombras en `@theme`.
- Variantes light/dark con variables CSS y `data-theme`.
- Clases de componentes en `@layer components` (`.btn-*`, `.table-*`, `.modal-*`, `.badge-*`, etc.).

Regla práctica:

- Si un patrón se repite (botones, filas, badges), crear clase semántica en `@layer components`.
- Si el uso es puntual, mantener utilidades Tailwind inline.

## Estado persistente en frontend

- Tema (`theme`) en `localStorage`.
- Sidebar (`sidebarCollapsed`) en `localStorage`.
- Página/fragmento en query params para conservar contexto en HTMX.

## Endpoints clave del módulo proveedores

- `GET /agrosol/proveedores/`
- `GET|POST /agrosol/proveedores/crear/`
- `GET|POST /agrosol/proveedores/editar/<id>/`
- `GET /agrosol/proveedores/confirmar/<id>/`
- `POST /agrosol/proveedores/eliminar/<id>/`
- `GET /agrosol/api/proveedores/opciones/`

## Resultados sugeridos para screenshots (agregar aquí capturas)

### Vista: listado de proveedores (desktop)

### Vista: listado de proveedores (mobile cards)

### Modal: crear proveedor

### Modal: editar proveedor

### Modal: confirmar eliminación

### Componente: popover de acciones por fila

### Componentes base: botones, inputs, badges, alerts

### Layout: topbar + sidebar (abierta y colapsada)

### Tema: light vs dark

## Troubleshooting rápido

### Cambios CSS no aparecen

- Verifica watcher de Tailwind activo.
- Recompila manualmente `input.css -> output.css`.
- Hard refresh del navegador.

### HTMX no actualiza el target esperado

- Revisa `hx-target` y que el selector exista.
- Confirma que la vista está retornando el partial correcto (`#table`, `#table_rows`, etc.).
- Revisa query params (`fragment`, `page`, `viewport`).

### Modal no carga contenido

- Valida que el botón tenga `data-action="openModal"` y `hx-get`.
- Confirma que exista `<div id="<modal>-content">`.
- Revisa errores JS en consola.

## Notas de mantenimiento

- `client/static/css/output.css` es compilado: no editar manualmente.
- Si agregas o renombras classes en templates, recompila Tailwind.
- Mantén los contratos de `utils.py` estables para no romper `partials/tables.html`.
- Prefiere comentarios breves de intención en código crítico (views, contracts, HTMX targets).
