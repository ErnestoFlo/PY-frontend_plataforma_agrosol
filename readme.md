# 🌾 AGROSOL - Documentación Frontend

**Última Actualización:** Abril 2026  
**Versión:** 1.0  
**Desarrollado con:** Django + Tailwind CSS + HTMX + JavaScript Vanilla

---

## 📚 TABLA DE CONTENIDOS

1. [Inicio Rápido](#inicio-rápido)
2. [Arquitectura General](#arquitectura-general)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Estructura de Carpetas](#estructura-de-carpetas)
5. [Sistema de Diseño (Tailwind)](#sistema-de-diseño-tailwind)
6. [Componentes Reutilizables](#componentes-reutilizables)
7. [Vistas y Lógica Backend](#vistas-y-lógica-backend)
8. [JavaScript - UI Interactions](#javascript--ui-interactions)
9. [Formularios Django](#formularios-django)
10. [Dependencias y Setup](#dependencias-y-setup)
11. [Guía de Modificación](#guía-de-modificación)
12. [Troubleshooting](#troubleshooting)

---

## 🚀 INICIO RÁPIDO

### Pré-requisitos
```bash
# Python 3.9+
# Node.js (para Tailwind CSS)
# pip instalado
```

### Setup Inicial
```bash
# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Ejecutar migraciones
python manage.py migrate

# 3. En una segunda terminal, compilar Tailwind CSS (watch mode)
.\tailwindcss.exe -i ./client/static/css/input.css -o ./client/static/css/output.css --watch

# 4. En una tercera terminal, correr servidor Django
python manage.py runserver

# 5. Abrir navegador en http://localhost:8000/agrosol/proveedores/
```

### Estructura Mínima Entendida
```
Archivo: views.py
    └─ Función: list_proveedores()
       └─ Llama a: utils.py → get_proveedores_for_table()
          └─ Retorna: dict con 'rows', 'total_pages', 'current_page'
             └─ Renderiza: template → proveedores/index_proveedores.html
                └─ Incluye: partials/tables.html#table
                   └─ Incluye: components/sidebar_item.html para cada menu item

Archivo: ui.js
    └─ DOMContentLoaded
       └─ Registra event listeners por data-action
          └─ Cada botón/input dispara función correspondiente
```

---

## 🏗️ ARQUITECTURA GENERAL

### Patrón MVC Extendido

```
┌─────────────────────────────────────────────────────────────┐
│                      NAVEGADOR (HTML/CSS/JS)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐    ┌────────────┐ │
│  │  Templates   │      │  Componentes │    │  ui.js     │ │
│  │  (Django)    │      │  (Partials)  │    │ (Eventos)  │ │
│  └──────┬───────┘      └──────┬───────┘    └────────────┘ │
│         │                     │                            │
│         └─────────────────────┴────────────────────────────┤
│                                                             │
├──────────────────────────────────────────────────────────────┤
│                   HTMX + Tailwind CSS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Django Backend (Python)                    │   │
│  │                                                   │   │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────────┐ │   │
│  │  │  views.py  │  │ utils.py │  │  forms.py    │ │   │
│  │  │  (Handlers)│  │(Helpers) │  │ (Validation) │ │   │
│  │  └────────────┘  └──────────┘  └──────────────┘ │   │
│  │                                                   │   │
│  │  ┌─────────────────────────────────────────────┐ │   │
│  │  │      services/proveedores.py (API calls)   │ │   │
│  │  └─────────────────────────────────────────────┘ │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                             │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────┐
    │   API Backend   │
    │   (C#, Node)    │
    │  192.168.1.55   │
    └─────────────────┘
```

### Flujo de Datos: Ejemplo Real

```
1. USER HACE CLICK "Eliminar" en tabla
   └─ Botón con: hx-get="/agrosol/proveedores/confirmar/123/" action="openModal"

2. HTMX intercepta
   └─ GET /agrosol/proveedores/confirmar/123/

3. DJANGO PROCESA
   └─ confirm_delete(request, id=123)
      └─ Retorna: confirm_delete.html#delete_proveedor partial
         └─ Variables: delete_url, table_body_id, row_id

4. HTMX RENDERIZA MODAL
   └─ Modal aparece con form POST{{ delete_url }}

5. USER CONFIRMA
   └─ Click → POST /agrosol/proveedores/eliminar/123/

6. DJANGO EJECUTA
   └─ delete_proveedor(request, id=123)
      └─ proveedores.delete(123)  # API DELETE call
      └─ get_proveedores_for_table(...)  # Obtiene lista actualizada
      └─ Retorna: table rows actualizado

7. HTMX REEMPLAZA
   └─ innerHTML="#tabla-prov-body" (tabla sin el eliminado)
   └─ hx-on::after-request → closeModal('modal-delete')

8. RESULTADO
   └─ Tabla actualizada, modal cerrada, sin page reload
```

---

## 🛠️ STACK TECNOLÓGICO

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Django** | Latest | Framework Web principal |
| **django-template-partials** | Latest | Componentes reutilizables en templates |
| **django-widget-tweaks** | Latest | Manipular atributos de widgets en templates |
| **Requests** | Latest | HTTP calls a API externa |

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **HTMX** | 1.9+ | Requests AJAX desde HTML |
| **Tailwind CSS** | 4.0+ | Sistema de diseño y clases utilitarias |
| **Flatpickr** | 4.6+ | Date/Time pickers customizados |
| **Swiper** | 11+ | Carruseles/sliders (si se necesitan) |
| **Vanilla JS** | ES6+ | Interacciones, event listeners |

### Build/Tooling
| Herramienta | Propósito |
|------------|-----------|
| **tailwindcss.exe** | Compilar CSS en watch mode |
| **input.css** | Archivo fuente que define temas y @directives |
| **output.css** | Archivo compilado (NO EDITAR MANUALMENTE) |

---

## 📁 ESTRUCTURA DE CARPETAS

```
client/
├── static/
│   ├── css/
│   │   ├── input.css          ← Editar: Define tema, colores, @import
│   │   ├── output.css         ← NO editar: Compilado por Tailwind
│   │   └── material_green.css ← OBSOLETO: No usar (dejado para referencia)
│   │
│   ├── js/
│   │   ├── ui.js              ← Interacciones UI principales
│   │   ├── htmx.min.js        ← HTMX library (NO editar)
│   │   ├── swiper-bundle.min.js ← Swiper library (NO editar)
│   │   ├── flatpickr.js       ← Flatpickr library + config (NO editar)
│   │   ├── es.js              ← Localización española Flatpickr (NO editar)
│   │   └── [otros]
│   │
│   ├── fonts/
│   │   ├── Montserrat-VariableFont_wght.woff2
│   │   └── Outfit-VariableFont_wght.woff2
│   │
│   └── images/
│       ├── sprite.svg         ← Iconos SVG (usar con <use href="#icon-name"/>)
│       └── [logos]
│
├── templates/
│   ├── base.html              ← Template root: incluye CSS/JS globales
│   │
│   ├── layouts/
│   │   ├── pc_nav.html        ← Layout principal: grid sidebar + main
│   │   ├── login.html         ← Login (sin sidebar)
│   │   ├── welcome.html       ← Bienvenida
│   │   └── [otros]
│   │
│   ├── components/            ← Componentes reutilizables (partials)
│   │   ├── sidebar.html       ← Sidebar con loop de menu_items
│   │   ├── sidebar_item.html  ← Un ítem del menu (reutilizable)
│   │   ├── topbar.html        ← Header superior
│   │   ├── buttons.html       ← Variantes de botones
│   │   ├── inputs.html        ← Campos de input
│   │   ├── modals.html        ← Estructura base de modales
│   │   ├── alerts.html        ← Alertas/notificaciones
│   │   └── [otros: avatars, badges, popovers]
│   │
│   ├── partials/              ← Partes funcionales de páginas
│   │   ├── tables.html        ← Tabla con paginación + filas
│   │   ├── options_lists.html ← Opciones de combobox (HTMX)
│   │   └── [otros: KPI_cards, log_list]
│   │
│   └── proveedores/           ← Templates de módulo Proveedores
│       ├── index_proveedores.html ← Listado
│       ├── form.html              ← Crear/Editar (unificado)
│       └── confirm_delete.html    ← Modal de confirmación
│
├── views.py                   ← Handlers de requests
├── utils.py                   ← Helper functions (paginación, menú, etc)
├── forms.py                   ← Validación de formularios  
├── models.py                  ← (Vacío: API-first architecture)
├── urls.py                    ← Rutas y endpoints
├── services/
│   └── proveedores.py         ← API calls a backend
└── [otros archivos de Django]
```

---

## 🎨 SISTEMA DE DISEÑO (TAILWIND)

### 1. CONFIGURACIÓN CENTRALIZADA: `input.css`

**Ubicación:** `client/static/css/input.css`

**¿Qué contiene?**
```css
@import "tailwindcss";              ← Importa Tailwind base
@source "../templates";             ← Busca templates para PurgeCSS
@theme { /* Color palette */ }      ← Define colores personalizados
@font-face { /* Tipografías */ }   ← Define fuentes
```

**Colores Definidos:**
```
PRIMARY-500:    Verde principal (#1CA347)
ACCENT-500:     Naranja secundario (#F98316)
SUCCESS/ERROR/WARNING/INFO:  Colores de estado
```

**Flujo de Compilación:**
```
input.css (source)
    ↓
tailwindcss.exe -i input.css -o output.css
    ↓
output.css (compilado ~ 400KB)
    ↓ (Browser carga)
Estilos en página
```

### 2. NOMBRES DE CLASES TAILWIND

**Convención:** `{propiedad}-{valor}`

```html
<!-- Layout -->
<div class="flex gap-3 p-4">       <!-- Flexbox, gap, padding -->
<div class="grid grid-cols-12">    <!-- CSS Grid, 12 columnas -->
<div class="w-full h-screen">      <!-- Width full, height screen -->

<!-- Colores -->
<button class="bg-primary-500 text-white">  <!-- Background + text color -->
<div class="border-primary-200 border-2">   <!-- Border color + width -->

<!-- Responsive -->
<div class="md:w-1/2 lg:w-1/3">    <!-- Media query: medium/large -->
<div class="hover:bg-primary-600"> <!-- Pseudo-class -->

<!-- Utilidades -->
<div class="rounded-xl shadow-lg">  <!-- Border radius, sombra -->
<p class="font-semibold text-sm">  <!-- Font weight, tamaño -->
```

### 3. CUSTOM CLASSES (Definidas en `input.css`)

```css
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-semibold transition-colors;
  }
  .btn-primary {
    @apply bg-primary-500 text-white hover:bg-primary-600;
  }
  .table-td {
    @apply px-4 py-2 text-sm text-fg-body border-bottom;
  }
  /* ... y muchas más */
}
```

**¿Por qué?**
- Agrupa clases repetidas → DRY
- Facilita cambios globales (cambiar `.btn` cambia todos los botones)
- Mantiene HTML limpio

### 4. VARIABLES CSS (Dark Mode)

```html
<!-- en base.html DOMContentLoaded -->
<script>
  const theme = localStorage.getItem('theme') || 'light'
  document.documentElement.setAttribute('data-theme', theme)
</script>
```

```css
/* En Tailwind config */
:root[data-theme="light"] {
  --color-bg: white;
  --color-fg: #1a1a1a;
}
:root[data-theme="dark"] {
  --color-bg: #1a1a1a;
  --color-fg: white;
}
```

**Toggling tema:**
```javascript
function toggleTheme() {
  const html = document.documentElement
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
  html.setAttribute('data-theme', next)
  localStorage.setItem('theme', next)
}
```

---

## 🧩 COMPONENTES REUTILIZABLES

### Anatomía de un Componente

**Ubicación:** `client/templates/components/`

```django
{% load partials %}

{% partialdef NOMBRE_COMPONENTE %}
  {# Documentación #}
  {# Variables esperadas:
     - variable1: Descripción
     - variable2: Descripción
  #}
  
  <html aqui>
    {% include "otros/componentes" %}
  </html>
{% endpartialdef %}
```

### Componentes Principales

#### 1. **BUTTON** (`buttons.html`)

**Uso:**
```django
{% include "components/buttons.html#button" with 
  func_type='button'
  type='btn-primary'
  text='Click Me'
  x_params='w-full'
  action='openModal'
  target='modal-id'
%}
```

**Parámetros:**
- `func_type`: `'button'` o `'submit'`
- `type`: `'btn-primary'`, `'btn-ghost'`, `'btn-danger'`, etc
- `text`: Texto mostrado
- `x_params`: Clases Tailwind adicionales
- `action`: `'openModal'`, `'closeModal'`, `'toggleTheme'`, etc
- `target`: ID del elemento target (ej: modal-id)
- `hx_get`/`hx_post`: URL para HTMX (opcional)

**Con HTMX:**
```django
{% include "components/buttons.html#button" with 
  func_type='button'
  type='btn-primary'
  text='Load Data'
  hx_get='/api/data/'
  hx_target='#data-container'
  hx_swap='innerHTML'
%}
```

#### 2. **INPUT** (`inputs.html`)

**Uso:**
```django
{% include "components/inputs.html#input" with
  field=form.email
  name='email'
  label='Email'
  type='email'
  x_params='col-span-6'
%}
```

**Renderiza:**
```html
<div class="col-span-6">
  <label for="email">Email</label>
  <input type="email" name="email" id="email" ... />
</div>
```

#### 3. **MODAL** (`modals.html`)

**Uso:**
```django
{% include "components/modals.html#modal" with
  modal_id='modal-delete'
  title='Confirmar eliminación'
  size='modal-md'
  show_footer=False
%}
```

**Estructura:**
```html
<div id="modal-delete" class="modal-overlay hidden">
  <div class="modal modal-md">
    <h2>Confirmar eliminación</h2>
    <div id="modal-delete-content">
      {# HTMX renderizará contenido aquí #}
    </div>
  </div>
</div>
```

**Interacción:**
```html
<!-- Botón para abrir -->
<button data-action="openModal" data-target="modal-delete">
  Eliminar
</button>

<!-- ui.js atrapa click y ejecuta: -->
<script>
  function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden')
  }
</script>
```

---

#### 4. **SIDEBAR_ITEM** (`sidebar_item.html`)

**Nuevo componente reutilizable** - Refactorización DRY

```django
{% include "components/sidebar_item.html#sidebar_item" with
  url='proveedores'
  icon_name='icon-pencil-regular'
  label='Proveedores'
  is_active=True
%}
```

**¿Por qué existe?**
- Antes: sidebar.html tenía 300+ líneas con 8+ IF/ELSE
- Ahora: sidebar.html hace loop sobre `menu_items`
- Componente renderiza cada ítem una sola vez

**En sidebar.html:**
```django
{% for item in menu_items %}
  {% include "components/sidebar_item.html#sidebar_item" with
    url=item.url
    icon_name=item.icon
    label=item.label
    is_active=item.is_active
  %}
{% endfor %}
```

#### 5. **TABLES** (`partials/tables.html`)

**Compleja** - Maneja: tabla + paginación + estado vacío

```django
{% include "partials/tables.html#table" with
  table_id='tabla-prov'
  columns=columns
  rows=rows
  current_page=current_page
  total_pages=total_pages
  page_range=page_range
  with_actions=True
%}
```

**Parámetros:**
- `table_id`: ID base para elementos (genera `tabla-prov-body`, etc)
- `columns`: Array de nombres de columnas
- `rows`: Array de filas {id, cells, edit_url, delete_url}
- `current_page`/`total_pages`: Para paginación
- `with_actions`: Mostrar columna de acciones (edit/delete)

**Renderizado interior:**
```html
<table>
  <thead>{{ columns }}</thead>
  <tbody id="tabla-prov-body">
    {% include "partials/tables.html#table_rows" %}
      (renderiza filas)
  </tbody>
</table>
{% include "partials/tables.html#table_pagination" %}
```

---

### Patrón de Inclusión

**Dos tipos principais:**

```django
{# 1. COMPLETO - Renderiza el componente #}
{% include "components/buttons.html#button" with ... %}

{# 2. PARTIAL - Referencia a un partialdef dentro del archivo #}
{% include "partials/tables.html#table_rows" %}
```

---

## 📡 VISTAS Y LÓGICA BACKEND

### Ubicación: `client/views.py`

**Organización:**
```python
# Vistas de Layout (sin lógica):
def welcome()      # /design/welcome/
def login()        # /design/login/
def view1()        # /design/dashboard/

# Vistas de Diseño/Testing:
def tests_components()  # /design/test_components/ - Demo de UI
def tests_form()        # /design/test_form/ - Demo de formularios
def get_options()       # /api/proveedores/opciones/ - Endpoint HTMX

# Vistas de Módulo Proveedores (CRUD):
def list_proveedores()           # GET /proveedores/ - Lista completa
def create_or_edit_proveedor()   # GET /crear/, POST /editar/<id>/ - Unificad
def delete_proveedor()           # POST /eliminar/<id>/ - Elimina
def confirm_delete()             # GET /confirmar/<id>/ - Modal
```

### Flujos Principales

#### **1. LIST - Obtener tabla paginada**

```python
def list_proveedores(request):
    # 1. Obtener datos de API
    proveedores_data = proveedores.get_all_proveedores()
    
    # 2. Helper: extrae datos + transforma + pagina
    page = int(request.GET.get('page', 1))
    table_context = get_proveedores_for_table(proveedores_data, page)
    # Retorna: {
    #    'rows': [...],
    #    'total_pages': 5,
    #    'current_page': 1,
    #    'page_range': [1, 2, 3, 4, 5]
    # }
    
    # 3. Si es HTMX (paginación): solo filas
    if request.headers.get('HX-Request'):
        return render(request, 'partials/tables.html#table_rows', {
            **table_context,
            'with_actions': True
        })
    
    # 4. Si es GET normal: página completa
    return render(request, "proveedores/index_proveedores.html", {
        **table_context,
        'menu_items': build_menu_items('Proveedores'),
        'columns': [...],
        'create_url': '/agrosol/proveedores/crear/',
        ...
    })
```

#### **2. CREATE/EDIT - Unificado**

**¿Por qué en una sola función?**

```
ANTES:
  def create_proveedor()  (35 líneas)
  def edit_proveedor()    (38 líneas)
  └─ 90% código idéntico

DESPUÉS:
  def create_or_edit_proveedor(request, id=None)  (50 líneas)
  └─ id=None → CREATE, id=int → EDIT
  └─ Una sola lógica
```

**Flujo:**

```python
def create_or_edit_proveedor(request, id=None):
    form = None
    
    # POST: Procesar formulario
    if request.method == "POST":
        form = ProveedoresForm(request.POST)
        if form.is_valid():
            if id:
                proveedores.update(id, form.cleaned_data)  # PUT
            else:
                proveedores.create(form.cleaned_data)      # POST
            
            # Retornar tabla actualizada
            proveedores_data = proveedores.get_all_proveedores()
            table_context = get_proveedores_for_table(proveedores_data, page)
            return render(request, "partials/tables.html#table_rows", {
                **table_context,
                'with_actions': True
            })
    
    # GET: Renderizar form (vacío o pre-llenado)
    else:
        if id:
            proveedor = proveedores.get_by_id(id)
            form = ProveedoresForm(initial=proveedor["data"])
        else:
            form = ProveedoresForm()
    
    # Determinar variables dinámicas
    submit_url = f'/agrosol/proveedores/editar/{id}/' if id else '/agrosol/proveedores/crear/'
    modal_name = 'modal-edit' if id else 'modal-create'
    submit_text = 'Editar' if id else 'Crear'
    
    return render(request, "proveedores/form.html#form", {
        'form': form,
        'submit_url': submit_url,
        'modal_name': modal_name,
        'submit_text': submit_text,
        'proveedor_id': id,
    })
```

#### **3. DELETE - Con confirmación**

```python
def confirm_delete(request, id):
    """Renderiza modal de confirmación (GET)"""
    return render(request, 'proveedores/confirm_delete.html#delete_proveedor', {
        'delete_url': f"/agrosol/proveedores/eliminar/{id}/",
        'table_body_id': '#tabla-prov-body',
        'row_id': id,
    })

def delete_proveedor(request, id):
    """Elimina después de confirmación (POST)"""
    if request.method == "POST":
        proveedores.delete(id)  # API call
        
        # Retornar tabla actualizada
        proveedores_data = proveedores.get_all_proveedores()
        table_context = get_proveedores_for_table(proveedores_data, page)
        return render(request, "partials/tables.html#table_rows", {
            **table_context,
            'with_actions': True,
        })
```

---

## 🎬 JAVASCRIPT – UI INTERACTIONS

### Ubicación: `client/static/js/ui.js`

**Patrón Principal: Data-Attribute Driven**

```html
<!-- HTML: Define acciones con data attributes -->
<button data-action="openModal" data-target="modal-delete">
  Eliminar
</button>

<!-- JavaScript: Ejecuta función basada en data-action -->
<script>
  document.querySelectorAll('[data-action="openModal"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      openModal(e.currentTarget.dataset.target)
    })
  })
</script>
```

### Funciones Principales

#### 1. **MODAL**

```javascript
function openModal(modalId) {
  const modal = document.getElementById(modalId)
  if (!modal) return
  modal.classList.remove('hidden')         // Mostrar
  document.body.style.overflow = 'hidden'  // Evitar scroll
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId)
  if (!modal) return
  modal.classList.add('hidden')           // Ocultar
  document.body.style.overflow = ''       // Restaurar scroll
}

// Exponer globalmente (usado desde templates)
window.closeModal = closeModal
```

**Uso en template:**
```html
{# Abrir modal #}
<button data-action="openModal" data-target="modal-create">
  + Nuevo
</button>

{# Cerrar desde dentro del modal (form) #}
<form hx-on::after-request="if(event.detail.successful) { closeModal('modal-create') }">
  ...
</form>
```

#### 2. **THEME (Dark Mode)**

```javascript
function toggleTheme() {
  const html = document.documentElement
  const current = html.getAttribute('data-theme')
  const next = current === 'dark' ? 'light' : 'dark'
  
  html.setAttribute('data-theme', next)      // Cambiar atributo
  localStorage.setItem('theme', next)        // Persistir elección
  updateThemeAssets(next)                    // Actualizar ícono/logo
}

function updateThemeAssets(theme) {
  const icon = document.querySelector('[data-action="toggleTheme"] use')
  const logo = document.querySelector('#main-logo')
  
  icon.setAttribute('href', theme === 'dark' 
    ? '/sprite.svg#icon-sun-regular'
    : '/sprite.svg#icon-moon-regular'
  )
  
  logo.setAttribute('src', theme === 'dark'
    ? '/static/images/logo-blanco@4x.png'
    : '/static/images/logo-color@4x.png'
  )
}
```

#### 3. **SIDEBAR**

```javascript
function collapseSidebar(btn) {
  const sidebarId = btn.dataset.target
  const sidebar = document.getElementById(sidebarId)
  
  const isCollapsed = sidebar.dataset.collapsed === 'true'
  sidebar.dataset.collapsed = isCollapsed ? 'false' : 'true'
  
  // CSS Tailwind: w-56 data-[collapsed=true]:w-15
  // Cuando collapsed=true, sidebar se hace angosto
}
```

#### 4. **COMBOBOX (SELECT DINÁMICO)**

```javascript
function comboboxToggle(trigger) {
  const targetId = trigger.dataset.target + '-options'
  const dropdown = document.getElementById(targetId)
  
  if (!dropdown) return
  
  // Toggle: mostrar/ocultar opciones
  dropdown.classList.contains('hidden')
    ? dropdown.classList.remove('hidden')
    : dropdown.classList.add('hidden')
}

// Seleccionar opción (delegación: las opciones se inyectan con HTMX)
document.addEventListener('click', (e) => {
  const option = e.target.closest('[data-action="combobox-select"]')
  if (!option) return
  
  const dropdown = option.closest('ul')
  const inputId = dropdown.dataset.input
  const input = document.getElementById(inputId)
  
  input.value = option.dataset.value
  dropdown.classList.add('hidden')
})
```

**Uso:**
```html
<input type="hidden" id="proveedor-id" />
<button data-action="comboboxToggle" data-target="proveedor">
  Seleccionar proveedor
</button>

<ul id="proveedor-options" data-input="proveedor-id" class="hidden">
  {# HTMX inyectará opciones aquí #}
  <li data-action="combobox-select" data-value="123">Agro Inc</li>
  <li data-action="combobox-select" data-value="456">Farm Ltd</li>
</ul>
```

**HTMX Integration:**
```html
<!-- Botón que dispara carga de opciones -->
<button hx-get="/api/proveedores/opciones/" 
        hx-target="#proveedor-options"
        hx-trigger="click"
        hx-swap="innerHTML">
  Cargar...
</button>

<!-- Después, HTMX renderiza opciones y dispara htmx:afterSwap -->
<!-- ui.js escucha: -->
document.addEventListener('htmx:afterSwap', (e) => {
  const dropdown = e.target.closest('.combobox-dropdown')
  if (!dropdown) return
  dropdown.classList.remove('hidden')
})
```

#### 5. **FORM INPUTS**

```javascript
function togglePassword(btn) {
  const inputId = btn.dataset.target
  const input = document.getElementById(inputId)
  const isPassword = input.type === 'password'
  
  input.type = isPassword ? 'text' : 'password'
  
  // Cambiar ícono
  const icon = btn.querySelector('use')
  icon.setAttribute('href',
    isPassword
      ? '/sprite.svg#icon-close-eye'
      : '/sprite.svg#icon-open-eye'
  )
}

function rangeUpdate(input, fill, thumb, output) {
  const min = parseFloat(input.min) || 0
  const max = parseFloat(input.max) || 100
  const val = parseFloat(input.value)
  const pct = ((val - min) / (max - min)) * 100
  
  fill.style.width = `${pct}%`
  thumb.style.left = `${pct}%`
  if (output) output.value = val
}
```

#### 6. **POPOVER**

```javascript
function togglePopover(popoverId) {
  const popover = document.getElementById(popoverId)
  const isOpen = popover.dataset.open === 'true'
  
  // Cerrar todos los demás
  document.querySelectorAll('.popover').forEach(p => 
    p.setAttribute('data-open', 'false')
  )
  
  // Toggle este
  popover.setAttribute('data-open', isOpen ? 'false' : 'true')
}

// Cerrar al click externo
document.addEventListener('click', (e) => {
  if (!e.target.closest('[data-action="popoverContainer"]')) {
    document.querySelectorAll('.popover').forEach(p => 
      p.setAttribute('data-open', 'false')
    )
  }
})
```

### Ciclo de Vida

```
DOMContentLoaded
  ↓
Registrar event listeners
  ├─ Botones con data-action
  ├─ Inputs con data-action
  ├─ Modales
  └─ Formularios
  ↓
Usuario interactúa
  ├─ Click → dispara listener
  ├─ setTimeout/HTMX → efectos visuales
  └─ API call (vía HTMX o fetch)
  ↓
Actualizar DOM
  ├─ Modal abierto/cerrado
  ├─ Estilo cambiado
  └─ Contenido reemplazado (HTMX)
```

---

## 📝 FORMULARIOS DJANGO

### Ubicación: `client/forms.py`

**Objeto:** ProveedoresForm

```python
class ProveedoresForm(forms.Form):
    """
    Formulario para crear/editar proveedores.
    
    Validación:
    - email: EmailValidator
    - proveedor: Required, max 240
    - direccion: Required, max 720
    ...
    """
    
    proveedor = forms.CharField(
        max_length=240,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre'})
    )
    
    email = forms.EmailField(
        max_length=400,
        required=True,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    
    # ... otros campos
```

### Flujo de Validación

```
1. User envía form
   └─ POST /agrosol/proveedores/crear/

2. Django recibe
   └─ create_or_edit_proveedor(request, id=None)
      └─ form = ProveedoresForm(request.POST)

3. Form valida
   └─ email: ¿válido?
   └─ proveedor: ¿máx 240?
   └─ todos required: ¿presentes?

4. Si VÁLIDO
   └─ form.is_valid() → True
   └─ form.cleaned_data contiene datos sanitizados
   └─ Enviar a API: proveedores.create(form.cleaned_data)

5. Si INVÁLIDO
   └─ form.is_valid() → False
   └─ form.errors contiene errores
   └─ Retornar form con errores mostrados
```

### Rendering en Template

```django
{% include "components/inputs.html#input" with
  field=form.email
  name='email'
  label='Correo electrónico'
  type='email'
  x_params='col-span-12'
%}

<!-- El componente renderiza: -->
<!-- <label for="email">Correo electrónico</label> -->
<!-- <input type="email" name="email" id="email" value="..." required> -->
<!-- {% if form.email.errors %} -->
<!--   <span class="error">{{ form.email.errors }}</span> -->
<!-- {% endif %} -->
```

---

## 📦 DEPENDENCIAS Y SETUP

### 1. Python Dependencies (`pip`)

```bash
# requirements.txt

django>=4.2                      # Framework web
django-template-partials>=0.9    # Componentes reutilizables
django-widget-tweaks>=1.4        # Manipular widgets en templates
requests>=2.31                   # HTTP calls (API)
djangorestframework>=3.14        # (Instalado, puede no usarse)
django-crispy-forms>=2.1         # (Instalado, no usado en este proyecto)
crispy-tailwind
```

**Instalación:**
```bash
pip install -r requirements.txt
```

### 2. Frontend Dependencies

**HTMX** (vía CDN o local: `client/static/js/htmx.min.js`)
```
Versión: 1.9+
Uso: AJAX requests desde HTML
Instalado: ✓ Local
```

**Tailwind CSS** (vía compilador)
```
Versión: 4.0+
Setup: tailwindcss.exe (ejecutable Windows)
Compilación: input.css → output.css
Instalado: ✓ Local
```

**Flatpickr** (para date pickers)
```
Versión: 4.6+
Instalado: ✓ Local (client/static/js/)
Uso: $("#fecha").flatpickr({...})
```

**Swiper** (para carruseles, si se usan)
```
Versión: 11+
Instalado: ✓ Local
Uso: new Swiper('.slider', {...})
```

### 3. Configuración Tailwind

**Archivo:** `tailwind.config.js` (raíz del proyecto)

```javascript
module.exports = {
  content: [
    "./client/templates/**/*.html",         // Buscar clases aquí
  ],
  theme: {
    extend: {
      // Extensiones personalizadas
    },
  },
  plugins: [],
}
```

**¿Por qué?**
- `content`: Tailwind escanea estos archivos para encontrar clases usadas
- Genera CSS solo con clases usadas (optimización)
- Si añades clase nueva en template, Tailwind la detecta automáticamente

### 4. Compilación CSS

**Watch Mode (desarrollo):**
```bash
.\tailwindcss.exe -i ./client/static/css/input.css -o ./client/static/css/output.css --watch
```

**One-time (producción):**
```bash
.\tailwindcss.exe -i ./client/static/css/input.css -o ./client/static/css/output.css
```

---

## 🔧 GUÍA DE MODIFICACIÓN

### **Caso 1: Agregar nuevo campo a formulario**

```python
# 1. En views.py → create_or_edit_proveedor()
# Ya maneja automáticamente cualquier campo en el form

# 2. En forms.py
class ProveedoresForm(forms.Form):
    # ... campos existentes ...
    
    # AGREGAR:
    nuevo_campo = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nuevo campo'})
    )

# 3. En template (proveedores/form.html)
{% include "components/inputs.html#input" with
  field=form.nuevo_campo
  name='nuevo_campo'
  label='Nuevo Campo'
  type='text'
  x_params='col-span-6'
%}
```

### **Caso 2: Cambiar color primario**

```css
/* En client/static/css/input.css */
@theme {
  /* ANTES: */
  --color-primary-500: hsl(148 98% 30%);  /* Verde */
  
  /* DESPUÉS: */
  --color-primary-500: hsl(200 98% 30%);  /* Azul */
}
```

**Tailwind recompila automáticamente** (si está en watch mode).

### **Caso 3: Agregar ítem al menú**

```python
# En client/utils.py
MENU_ITEMS_CONFIG = [
    # ... items existentes ...
    
    # AGREGAR:
    {'url': 'clientes', 'icon': 'icon-user-regular', 'label': 'Clientes', 'page_name': 'Clientes'},
]

# En la vista correspondiente:
def list_clientes(request):
    return render(request, "clientes/index.html", {
        'menu_items': build_menu_items('Clientes'),  # ← match page_name
        ...
    })
```

### **Caso 4: Agregar nuevo componente**

```django
{# Crear: client/templates/components/mi_componente.html #}

{% load partials %}

{% partialdef mi_componente %}
  {# Documentación: variables esperadas #}
  {# - variable1: Descripción #}
  {# - variable2: Descripción #}
  
  <div> ... </div>
{% endpartialdef %}

{# Usar en otros templates: #}
{% include "components/mi_componente.html#mi_componente" with
  variable1=valor1
  variable2=valor2
%}
```

### **Caso 5: Agregar función JavaScript**

```javascript
// En client/static/js/ui.js

document.addEventListener('DOMContentLoaded', () => {
  // AGREGAR: Registrar event listeners
  document.querySelectorAll('[data-action="miAccion"]').forEach(element => {
    element.addEventListener('click', (e) => miFunction(e.currentTarget))
  })
  
  // AGREGAR: Función
  function miFunction(element) {
    // Realiza acción
    console.log('Ejecutada miFunction')
  }
  
  // Si necesita ser expuesta globalmente:
  window.miFunction = miFunction
})
```

**Uso en HTML:**
```html
<button data-action="miAccion">Click</button>
```

---

## 🩹 TROUBLESHOOTING

### **Problema: Cambios CSS no aparecen**

**Solución:**
1. Verificar que Tailwind está en watch mode: `.\tailwindcss.exe ... --watch`
2. Hard refresh navegador: `Ctrl+Shift+R`
3. Verificar que la clase está en `input.css` o es estándar Tailwind
4. Recompilar manualmente:
   ```bash
   .\tailwindcss.exe -i ./client/static/css/input.css -o ./client/static/css/output.css
   ```

### **Problema: Modal no abre**

**Checklist:**
1. ¿Button tiene `data-action="openModal"` y `data-target="modal-id"`?
2. ¿Modal existe con `id="modal-id"`?
3. ¿Hay error en JavaScript (F12 Console)?
4. Verificar que `ui.js` está cargado: `<script src=".../ui.js"></script>`

**Debug:**
```javascript
// En F12 Console:
openModal('modal-id')  // Ejecutar manualmente
```

### **Problema: HTMX no funciona**

**Checklist:**
1. ¿Tag tiene `hx-get`/`hx-post`?
2. ¿URL es válida? (probar en navegador)
3. ¿`hx-target` existe y selector es correcto?
4. ¿`hx-swap` es válido? (`innerHTML`, `outerHTML`, `beforeend`…)
5. Ver Network tab (F12 → Network) → Request fallido?

**Debug:**
```html
<!-- Agregar logging: -->
<button hx-get="/api/data/" 
        hx-target="#data"
        hx-trigger="click"
        hx-on::after-request="console.log(event)">
  Load
</button>
```

### **Problema: Form no valida en backend**

**Verificar:**
1. En views.py: `form.is_valid()` → False?
2. `form.errors` contiene detalles:
   ```python
   if not form.is_valid():
       print(form.errors)  # Ver qué falta
   ```
3. ¿Email válido? Test: `test@example.com`
4. ¿Campo required está presente en POST?

### **Problema: JavaScript lanza undefined error**

**Causas comunes:**
1. Elemento no existe en DOM: `getElementById('id')` retorna `null`
   - Solución: Agregar `if (!element) return` al inicio de función

2. Variable definida fuera de scope:
   - Asegurar que está dentro de `DOMContentLoaded`

3. Typo en nombre de función:
   - Ver `window.closeModal` vs `closeModal`

**Debug:**
```javascript
// F12 Console:
typeof openModal  // Debe ser 'function'
document.getElementById('modal-id')  // Debe retornar elemento
```

---

## 📚 RESUMEN RÁPIDO

**Para nuevo developer:**

| Necesidad | Dónde | Cómo |
|-----------|-------|------|
| Entender flujo | `views.py` | Leer función principal |
| Agregar botón | `components/buttons.html` | Include con parámetros |
| Cambiar color | `input.css` | Editar @theme |
| Agregar ítem menú | `utils.py` | Agregar a MENU_ITEMS_CONFIG |
| Debug JavaScript | Browser F12 | Console + Network |
| Recompilar CSS | Terminal | `tailwindcss.exe --watch` |
| Ver variables form | `forms.py` | Leer definición de Form |
| Editar tabla | `partials/tables.html` | Modificar estructura HTML |

---

## 📞 CONTACTO / PREGUNTAS

Para dudas sobre:
- **Diseño/CSS**: Ver `input.css` y `tailwind.config.js`
- **Componentes**: Ver archivos en `templates/components/`
- **Lógica Backend**: Ver `views.py` y `utils.py`
- **Interacciones**: Ver `ui.js` y patrón data-action

---

**Documento creado:** Abril 2026  
**Proyecto:** AGROSOL - De la Mano con el Agricultor  
**Stack:** Django + Tailwind CSS + HTMX + Vanilla JS
