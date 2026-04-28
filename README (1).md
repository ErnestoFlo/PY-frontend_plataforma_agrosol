# 🌱 Agrosol — Frontend Platform
### Sprint de Desarrollo: Sistema de Usuarios, Permisos y Trazabilidad

---

## 📋 Tabla de Contenidos

1. [Stack y Tecnologías](#stack-y-tecnologías)
2. [Dependencias](#dependencias)
3. [Novedades de esta versión](#novedades-de-esta-versión)
4. [Arquitectura del sistema](#arquitectura-del-sistema)
5. [Tutorial de implementación](#tutorial-de-implementación-para-próximas-versiones)
6. [Resultados obtenidos](#resultados-obtenidos)

---

## Stack y Tecnologías

| Capa | Tecnología | Versión |
|---|---|---|
| Backend framework | Django | 5.1.7 |
| Lenguaje | Python | 3.13 |
| Base de datos | MySQL | — |
| ORM / Driver MySQL | MySQLdb | — |
| Frontend CSS | Bootstrap | 5.3.8 |
| Iconos | Bootstrap Icons | 1.11.0 |
| Tipografía | DM Mono + Syne | Google Fonts |
| Parseo HTML | BeautifulSoup4 | 4.x |
| Servidor de desarrollo | Django runserver | — |
| API externa | REST (SSL deshabilitado) | `https://192.168.1.55:7155/api/` |

### Tema visual
Dark theme consistente con paleta verde (`#4ade80`) sobre fondo casi negro (`#0a0f0a`), tipografía `Syne` para UI y `DM Mono` para datos técnicos y código.

---

## Dependencias

### Python (requirements)
```
Django==5.1.7
mysqlclient
beautifulsoup4
Pillow              # manejo de imágenes / avatares
```

### Instalación
```bash
pip install Django mysqlclient beautifulsoup4 Pillow
```

### Estructura de la aplicación
```
frontend/                       ← proyecto Django
├── frontend/
│   ├── settings.py
│   ├── urls.py                 ← handlers de error y URLs raíz
│   └── wsgi.py
└── client/                     ← app principal
    ├── models.py               ← todos los modelos del sistema
    ├── views.py                ← todas las vistas
    ├── urls.py                 ← URLs de la app
    ├── forms.py
    ├── signals.py              ← señales de login/logout
    ├── middleware.py           ← captura de acceso a módulos
    ├── apps.py                 ← conecta señales al arrancar
    ├── services/
    │   ├── api_client.py
    │   └── proveedores.py
    ├── management/
    │   └── commands/
    │       └── limpiar_logs.py ← comando de limpieza de logs
    ├── templates/
    │   ├── registration/
    │   │   └── login.html
    │   ├── client/
    │   │   ├── perfil.html
    │   │   ├── prueba_tecnica.html
    │   │   ├── permisos/
    │   │   │   └── panel.html
    │   │   └── usuarios/
    │   │       ├── lista.html
    │   │       ├── editar.html
    │   │       ├── confirmar_desactivar.html
    │   │       └── logs_usuario.html
    │   ├── logs/
    │   │   └── logs_modulo.html
    │   ├── proveedores/
    │   └── errors/
    │       ├── 400.html
    │       ├── 403.html
    │       ├── 404.html
    │       └── 500.html
    └── templatetags/
        ├── __init__.py
        └── dict_extras.py
```

---

## Novedades de esta versión

### 1. 🔐 Sistema de Autenticación
- Login/Logout con `django.contrib.auth`
- Logout requiere `POST` (seguridad Django 5+)
- **Cierre de sesión por inactividad**: modal con cuenta regresiva de 60 segundos tras 30 minutos sin actividad
- Configuración de sesión: `SESSION_EXPIRE_AT_BROWSER_CLOSE=True`, `SESSION_COOKIE_AGE=28800`

### 2. 👤 UserProfile extendido
Modelo que extiende al `User` de Django con campos adicionales:
- `avatar` (imagen de perfil)
- `cargo`, `area`, `telefono`
- Se crea automáticamente via **signals** `post_save`

### 3. 👥 Gestión de Usuarios (solo Superusuarios)
- Lista de usuarios con búsqueda en tiempo real
- **Crear usuario desde modal** sin recargar página (fetch + FormData)
- Editar usuario con toggles de `is_staff` / `is_superuser`
- Soft delete: desactivación (`is_active=False`) sin borrar datos
- Regla de negocio: **un usuario = un solo grupo** (se aplica con `groups.clear()` antes de asignar)

### 4. 🛡️ Sistema de Permisos Granulares (2 niveles)

#### Nivel 1 — Acceso al módulo
```
AccesoModulo(group, modulo, tiene_acceso)
```
Controla si el grupo puede entrar a la pantalla. Si no tiene acceso → **403**.

#### Nivel 2 — Permisos de elementos
```
PermisoElemento(group, elemento, puede_ver, puede_usar)
```
Controla qué elementos dentro del módulo puede ver y usar el grupo.

#### Lógica de permisos
| Estado | Resultado visual |
|---|---|
| `ver=True, usar=True` | Elemento funciona normal |
| `ver=True, usar=False` | Elemento visible pero deshabilitado (opacidad 35%, `pointer-events:none`) |
| `ver=False` | Elemento no existe en el DOM |

#### Tipos de elementos
| Tipo | Color | Descripción |
|---|---|---|
| `accion` | 🔴 Naranja | Botones que ejecutan operaciones |
| `componente` | 🔵 Azul | Inputs que reciben datos |
| `dato` | 🟢 Verde | Tablas y columnas que muestran información |

### 5. 🧩 Panel de Permisos
Panel visual para superusuarios con dos tabs:

**Tab Grupos:**
- Crear / eliminar grupos
- Asignar usuarios a grupos (con indicador visual del grupo actual)
- Asignar módulos a grupos con un modal
- Configurar permisos de elementos por grupo (toggles VER/USAR)

**Tab Módulos:**
- Crear módulos con nombre, ícono (Bootstrap Icons), `url_name` y descripción
- Editar módulos
- **Escaneo automático de templates**: detecta todos los elementos con `data-permiso` en el HTML y los registra en la BD
- Ver qué grupos tienen acceso a cada módulo

### 6. 🔍 Detección Automática de Elementos
Los templates marcan sus elementos interactivos con atributos HTML:
```html
<button data-permiso="btn_crear"
        data-tipo="accion"
        data-label="Botón Crear">
  Crear
</button>
```
El sistema escanea el template, encuentra estos atributos y registra automáticamente los `Elemento` en la BD sin configuración manual.

### 7. 📊 Sistema de Activity Logs
Registro completo de actividad del usuario con los siguientes tipos de evento:

| Evento | Captura | Método |
|---|---|---|
| `login` | Inicio de sesión | Signal Django |
| `logout` | Cierre de sesión | Signal Django |
| `modulo` | Acceso a pantalla | Middleware automático |
| `elemento` | Interacción con UI | Fetch desde JS |
| `crear` | Creación de datos | Decorador `@registrar_actividad` |
| `editar` | Edición de datos | Decorador `@registrar_actividad` |
| `eliminar` | Eliminación de datos | Decorador `@registrar_actividad` |
| `buscar` | Búsquedas y consultas | Decorador `@registrar_actividad` |
| `acceso_denegado` | Intento de acceso 403 | Vista de error |

Cada log registra: usuario, tipo, módulo, elemento, descripción, IP y dispositivo (navegador/SO).

**Limpieza automática:**
```bash
python manage.py limpiar_logs --dias=90       # borra logs de más de 90 días
python manage.py limpiar_logs --dry-run       # preview sin borrar
```

### 8. 📄 Páginas de Error Personalizadas
- `400.html` — amarillo, causas posibles
- `403.html` — rojo, candado animado, muestra usuario conectado
- `404.html` — índigo, animación flotante, muestra la URL
- `500.html` — naranja, efecto glitch, terminal animada

---

## Arquitectura del Sistema

### Modelos principales

```python
UserProfile          # extiende User con avatar, cargo, área, teléfono
Modulo               # pantalla del sistema (nombre, slug, icono, url_name)
Elemento             # elemento dentro de un módulo (clave, tipo, label)
AccesoModulo         # grupo → módulo (tiene_acceso: bool)
PermisoElemento      # grupo → elemento (puede_ver, puede_usar: bool)
ActivityLog          # registro de actividad del usuario
```

### Helpers principales

```python
# models.py
tiene_acceso_modulo(user, url_name)   # → bool  (Nivel 1)
get_permisos(user, url_name)          # → dict  (Nivel 2)
registrar_log(request, tipo, ...)     # registra un evento
registrar_actividad(accion, modelo)   # decorador para vistas CRUD

# Ejemplo dict de get_permisos:
{
  'btn_crear':   {'ver': True,  'usar': True,  'tipo': 'accion'},
  'c_textbox':   {'ver': True,  'usar': False, 'tipo': 'componente'},
  'tabla_datos': {'ver': False, 'usar': False, 'tipo': 'dato'},
}
```

### Flujo de protección de vistas

```
Request del usuario
        ↓
    @login_required          ← ¿está autenticado?
        ↓
tiene_acceso_modulo()        ← Nivel 1: ¿puede entrar al módulo?
        ↓                         NO → PermissionDenied → 403 (+ log)
get_permisos()               ← Nivel 2: ¿qué puede hacer dentro?
        ↓
render(template, {permisos}) ← El template decide qué mostrar
```

---

## Tutorial de Implementación para Próximas Versiones

### Cómo proteger una vista nueva

**Paso 1** — En `client/urls.py`, registrar la URL con un `name`:
```python
path("mi-modulo/", views.mi_vista, name="mi_modulo"),
```

**Paso 2** — En `client/views.py`, agregar la protección:
```python
from .models import tiene_acceso_modulo, get_permisos, registrar_actividad

@login_required
def mi_vista(request):
    # Nivel 1: acceso al módulo
    if not tiene_acceso_modulo(request.user, 'mi_modulo'):
        raise PermissionDenied

    # Nivel 2: permisos de elementos
    permisos = get_permisos(request.user, 'mi_modulo')

    return render(request, 'mi_app/mi_vista.html', {'permisos': permisos})
```

**Paso 3** — En el template, marcar los elementos con `data-permiso`:
```html
<!-- ACCIÓN -->
{% if not permisos or permisos.btn_crear.ver %}
<button data-permiso="btn_crear"
        data-tipo="accion"
        data-label="Botón Crear"
        {% if permisos and not permisos.btn_crear.usar %}disabled{% endif %}>
  Crear
</button>
{% endif %}

<!-- COMPONENTE -->
{% if not permisos or permisos.c_nombre.ver %}
<input data-permiso="c_nombre"
       data-tipo="componente"
       data-label="Campo Nombre"
       class="{% if permisos and not permisos.c_nombre.usar %}perm-card-disabled{% endif %}">
{% endif %}

<!-- COLUMNA DE TABLA (dato) -->
{% if not permisos or permisos.col_total.ver %}
<th data-permiso="col_total" data-tipo="dato" data-label="Columna Total">Total</th>
{% endif %}
```

**Paso 4** — En el panel de permisos, crear el módulo:
1. Tab **Módulos** → Crear módulo con `url_name = mi_modulo`
2. Click en 🔍 para escanear el template → detecta los elementos automáticamente
3. Tab **Grupos** → Asignar el módulo al grupo → Configurar permisos de elementos

---

### Cómo agregar logs CRUD a una vista

```python
# Crear
@login_required
@registrar_actividad(accion='crear', modelo='Factura', campo_label='numero')
def crear_factura(request):
    ...

# Editar
@login_required
@registrar_actividad(accion='editar', modelo='Factura', campo_label='numero')
def editar_factura(request, id):
    ...

# Eliminar (funciona con GET o POST)
@login_required
@registrar_actividad(accion='eliminar', modelo='Factura')
def eliminar_factura(request, id):
    ...

# Búsqueda (captura el parámetro GET)
@login_required
@registrar_actividad(accion='buscar', modelo='Facturas', campo_busqueda='q')
def listar_facturas(request):
    ...
```

> ⚠️ El decorador `@registrar_actividad` siempre debe ir **después** de `@login_required`.

---

### Cómo agregar logs de búsqueda desde el frontend (buscadores JS)

Si el buscador filtra en tiempo real con JavaScript sin recargar la página, agregar este snippet en el template:

```javascript
let logTimer;
document.getElementById('mi-buscador').addEventListener('input', function() {
  const q = this.value.trim();
  clearTimeout(logTimer);
  if (q.length >= 2) {
    logTimer = setTimeout(() => {
      const fd = new FormData();
      fd.append('csrfmiddlewaretoken', '{{ csrf_token }}');
      fd.append('elemento_clave', 'buscar_mi_modelo');
      fd.append('elemento_label', `Buscó: "${q}"`);
      fd.append('modulo_url', 'mi_modulo');
      fetch('{% url "registro_elemento" %}', { method: 'POST', body: fd })
        .catch(() => {});
    }, 800); // espera 800ms para no loguear cada letra
  }
});
```

---

### Cómo agregar una carpeta nueva de templates al escaneo

El sistema detecta templates automáticamente usando el motor de Django. No requiere configuración — cualquier template dentro de las carpetas registradas en `settings.TEMPLATES` o en la carpeta `templates/` de cada app instalada será encontrado automáticamente.

---

### Configuración requerida en settings.py

```python
# Sesión
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE              = 28800  # 8 horas
SESSION_SAVE_EVERY_REQUEST      = True

# Media (avatares)
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Middleware (agregar al final)
MIDDLEWARE = [
    ...
    'client.middleware.ActivityLogMiddleware',
]

# Páginas de error (en frontend/urls.py, no settings)
handler400 = 'client.views.error_400'
handler403 = 'client.views.error_403'
handler404 = 'client.views.error_404'
handler500 = 'client.views.error_500'

# Para que las páginas de error funcionen:
DEBUG = False
```

---

### Comandos útiles

```bash
# Aplicar migraciones
python manage.py makemigrations client
python manage.py migrate

# Limpiar logs antiguos
python manage.py limpiar_logs --dias=90
python manage.py limpiar_logs --dry-run   # preview

# Shell — poblar módulo de prueba
python manage.py shell
# Pegar el script de creación de Modulo + Elemento del sprint
```

---

## Resultados Obtenidos

### ✅ Funcionalidades completadas

| Módulo | Estado | Descripción |
|---|---|---|
| Autenticación | ✅ Completo | Login, logout, sesión por inactividad |
| UserProfile | ✅ Completo | Avatar, cargo, área, teléfono |
| Gestión de usuarios | ✅ Completo | CRUD desde panel, modal de creación |
| Sistema de grupos | ✅ Completo | Un usuario = un grupo, gestión visual |
| Permisos Nivel 1 | ✅ Completo | Acceso/bloqueo por módulo |
| Permisos Nivel 2 | ✅ Completo | VER/USAR por elemento granular |
| Panel de permisos | ✅ Completo | Tabs grupos/módulos, escaneo automático |
| Detección automática | ✅ Completo | `data-permiso` + escaneo de templates |
| Páginas de error | ✅ Completo | 400, 403, 404, 500 personalizadas |
| Activity Logs | ✅ Completo | 9 tipos de evento, middleware + signals |
| Logs en perfil | ✅ Completo | Últimos 50 eventos con filtros |
| Logs admin | ✅ Completo | Vista por usuario con stats |
| Logs por módulo | ✅ Completo | Vista cronológica clasificada |
| Limpieza automática | ✅ Completo | Comando `limpiar_logs` |
| Prueba técnica | ✅ Completo | 27 elementos marcados y protegidos |

### 📐 Métricas del sprint

- **Modelos creados:** 6 (`UserProfile`, `Modulo`, `Elemento`, `AccesoModulo`, `PermisoElemento`, `ActivityLog`)
- **Vistas desarrolladas:** 25+
- **Templates creados:** 12
- **Elementos marcados en prueba técnica:** 27 (9 acciones, 11 componentes, 7 datos)
- **Tipos de log registrados:** 9
- **Capas de seguridad:** 3 (autenticación → acceso módulo → permisos elemento)

### 🏗️ Decisiones de arquitectura clave

**Un usuario = un solo grupo** — simplifica la gestión de permisos y hace el comportamiento predecible. Al asignar un nuevo grupo se hace `groups.clear()` automáticamente.

**Detección de elementos por `data-permiso`** — desacopla el sistema de permisos del código Python. El superadmin puede escanear cualquier template nuevo sin tocar el backend.

**Decorador `@registrar_actividad`** — el logging de CRUD es declarativo. Solo requiere una línea por vista, no hay que modificar la lógica interna.

**Middleware para logs de módulos** — captura automáticamente el acceso a pantallas sin modificar ninguna vista existente.

**`is not False` → evaluación correcta en Django templates** — los templates de Django no soportan el operador `is not False` de Python. La condición correcta es `{% if permisos.clave.ver %}`.

---

## 👨‍💻 Desarrollo

Sprint desarrollado para la plataforma Agrosol.
Stack: Django 5.1.7 · MySQL · Bootstrap 5.3.8 · Python 3.13
