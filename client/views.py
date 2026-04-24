from django.shortcuts import render, redirect
from .services import proveedores
from .forms import ProveedoresForm, LoginForm, SearchForm
from django.http import HttpResponse
from .utils import get_proveedores_for_table, build_menu_sidebar_items, build_menu_mobilebar_items
import urllib3

# Suprimir advertencia de HTTPS sin verificación de certificados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

########## VISTAS POR DISEÑO ###########

def landing_login(request):
    login_form = LoginForm()
    return render(request, "layouts/landing_login.html", {
        "pagename": "Bienvenida",
        'menu_sidebar_items': build_menu_sidebar_items('Bienvenida'),
        'menu_mobilebar_items': build_menu_mobilebar_items('Bienvenida'),
        'path': request.path,
        "form": login_form
    })


def view1(request):
    search_form = SearchForm()
    return render(request, "design/view1.html", {
        "pagename": "Dashboard",
        'menu_sidebar_items': build_menu_sidebar_items('Dashboard'),
        'menu_mobilebar_items': build_menu_mobilebar_items('Dashboard'),
        'path': request.path,
        "search_form": search_form
    })

def tests_form(request):
    return render(request, "design/main_form_test.html", {
        "pagename": "Main Form Test",
        'menu_sidebar_items': build_menu_sidebar_items('Main Form Test'),
        'menu_mobilebar_items': build_menu_mobilebar_items('Main Form Test'),
        'path': request.path
    })

def tests_components(request):
    page = int(request.GET.get('page', 1))
    per_page = 6

    test_rows = [
        {'id': i, 'avatar': True, 'initials': 'AB', 'cells': [
            'Cell Text', 'Cell Text', f'Cell Text that is loooooooooo...'
        ]} for i in range(1, 25)
    ]

    total = len(test_rows)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    paginated = test_rows[start:start + per_page]

    return render(request, 'design/components_test.html', {
        'rows': paginated,
        'columns': ['Avatar', 'Header', 'Long Text Column', 'Header'],
        'current_page': page,
        'total_pages': total_pages,
        'page_range': range(1, total_pages + 1),
        'pagename': 'Test & Views',
        'menu_sidebar_items': build_menu_sidebar_items('Test & Views'),
        'menu_mobilebar_items': build_menu_mobilebar_items('Test & Views'),
        'path': request.path
    })

def get_options(request):
    """
    Endpoint para obtener opciones dinámicas de un combobox.
    Usado por HTMX para inyectar/actualizar opciones de forma dinámica.
    """
    options = [
        {'id': 1, 'nombre': 'Opcion 1'},
        {'id': 2, 'nombre': 'Opcion 2'},
        {'id': 3, 'nombre': 'Opcion 3'},
        {'id': 4, 'nombre': 'Opcion 4'},
        {'id': 5, 'nombre': 'Opcion 5'}
    ]
    return render(request, 'partials/options_lists.html#combobox_options', {
        'options': [{'value': o['id'], 'label': o['nombre']} for o in options]
    })

########## VISTAS DE PROVEEDORES ##########
def list_proveedores(request):
    search_form = SearchForm(request.GET)
    proveedores_data = proveedores.get_all_proveedores()
    page = int(request.GET.get('page', 1))
    
    table_context = get_proveedores_for_table(proveedores_data, page)

    is_htmx = request.headers.get('HX-Request')
    fragment = request.GET.get('fragment')

    # 🔹 SOLO TABLA COMPLETA (para skeleton → carga inicial)
    if is_htmx and fragment == "table":
        return render(request, 'partials/tables.html#table', {
            **table_context,
            'with_actions': True,
            'table_id': 'tabla-prov',
            'columns': ['Proveedor', 'Dirección', 'Contacto', 'Cargo', 'Teléfono', 'Celular', 'Email', 'Términos de Pago'],
        })

    # 🔹 SOLO FILAS (paginación)
    if is_htmx:
        return render(request, 'partials/tables.html#table', {
            **table_context,
            'with_actions': True,
            'table_id': 'tabla-prov',
            'columns': ['Proveedor', 'Dirección', 'Contacto', 'Cargo', 'Teléfono', 'Celular', 'Email', 'Términos de Pago'],
        })

    # 🔹 Página completa (fallback normal)
    return render(request, "proveedores/index_proveedores.html", {
        **table_context,
        'create_url': '/agrosol/proveedores/crear/',
        'pagename': 'Proveedores',
        'columns': [...],
        'table_body_id': '#tabla-prov-body',
        'menu_sidebar_items': build_menu_sidebar_items('Proveedores'),
        'menu_mobilebar_items': build_menu_mobilebar_items('Proveedores'),
        'path': request.path,
        'search_form': search_form
    })

def create_or_edit_proveedor(request, id=None):
    """
    Crea O edita un proveedor - FUNCIÓN UNIFICADA.
    
    ¿POR QUÉ UNA SOLA FUNCIÓN?
    - create_proveedor() y edit_proveedor() eran 90% idénticas
    - El único cambio: POST → proveedores.create() vs PUT → proveedores.update(id, ...)
    - Consolidar elimina 40+ líneas de código duplicado
    
    RUTAS (en urls.py):
    - POST /agrosol/proveedores/crear           → create_or_edit_proveedor(id=None)
    - POST /agrosol/proveedores/editar/<id>    → create_or_edit_proveedor(id=<id>)
    
    ¿BACKEND SE ENTERA?
    - NO, el backend recibe exactamente lo mismo:
      - create_proveedor() → requests.POST → backend recibe POST /api/Proveedores
      - edit_proveedor(id) → requests.PUT → backend recibe PUT /api/Proveedores/<id>
    - El cambio es 100% frontend, transparente para backend
    
    FLU LÓGICO:
    1. GET /crear → Renderiza form vacío
    2. POST /crear + form válido → create() + retorna tabla actualizada
    3. GET /editar/<id> → Renderiza form pre-llenado con datos del proveedor
    4. POST /editar/<id> + form válido → update() + retorna tabla actualizada
    """
    form = None
    
    if request.method == "POST":
        form = ProveedoresForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            from .utils import build_table_rows
            
            # CREATE o UPDATE - Ambos retornan el objeto actualizado/creado
            if id:
                # EDITAR: actualiza el proveedor existente
                proveedores.update(id, form.cleaned_data)
                # UPDATE retorna solo confirmación sin datos
                # Necesitamos GET para obtener todos los datos del proveedor actualizado
                proveedor_response = proveedores.get_by_id(id)
                # get_by_id retorna {data: {...}} o directamente {...}
                proveedor_dict = proveedor_response.get("data", proveedor_response) if isinstance(proveedor_response, dict) else proveedor_response
            else:
                # CREAR: crea nuevo proveedor y retorna el objeto creado
                response_data = proveedores.create(form.cleaned_data)
                # CREATE retorna {success, data: {...proveedor completo...}}
                proveedor_dict = response_data.get("data", response_data) if isinstance(response_data, dict) else response_data
            
            # Construir UNA SOLA FILA con los datos del proveedor
            rows = build_table_rows([proveedor_dict]) if proveedor_dict else []
            
            if rows:
                return render(request, "partials/tables.html#table_rows", {
                    'rows': rows,
                    'with_actions': True,
                })
    else:
        # GET request
        if id:
            # Modo EDITAR: pre-llenar form con datos existentes
            proveedor_data = proveedores.get_by_id(id)
            form = ProveedoresForm(initial=proveedor_data["data"])
        else:
            # Modo CREAR: form vacío
            form = ProveedoresForm()
    
    # Renderizar template del formulario
    # Nota: Un solo template (form.html) maneja ambos casos (CREATE y EDIT)
    # Variables dinámicas determinan comportamiento:
    if id:
        # MODO EDITAR
        submit_url = f'/agrosol/proveedores/editar/{id}/'
        modal_name = 'modal-edit'
        submit_text = 'Editar'
    else:
        # MODO CREAR
        submit_url = '/agrosol/proveedores/crear/'
        modal_name = 'modal-create'
        submit_text = 'Crear'
    
    template = "proveedores/form.html#form"
    context = {
        "form": form,
        "proveedor_id": id,
        "submit_url": submit_url,
        "modal_name": modal_name,
        "submit_text": submit_text,
    }
    is_htmx = request.headers.get('HX-Request')
    fragment = request.GET.get('fragment')

    # 🔹 SOLO FORM (para skeleton → carga inicial)
    if is_htmx and fragment == "form":
        return render(request, template, context)
    else:
        return render(request, "proveedores/form.html#form", context)

def delete_proveedor(request, id):
    """
    Elimina un proveedor mediante POST (desde modal de confirmación).
    
    FLUJO:
    1. confirm_delete() renderiza modal con delete_url
    2. User hace click en "Confirmar"
    3. FORM hace POST hx-post="{{ delete_url }}"
    4. Esta función recibe POST, elimina item
    5. Retorna tabla actualizada
    6. HTMX reemplaza tabla + cierra modal
    
    ¿POR QUÉ POST EN LUGAR DE GET?
    - GET debe ser solo lectura (no debe tener side effects)
    - DELETE debe ser POST o HTTP DELETE method
    - POST incluye CSRF token automático
    - Más seguro y estándar REST
    
    SEGURIDAD:
    - CSRF token validado por middleware de Django
    - Solo acepta POST (no GET)
    """
    if request.method == "POST":
        # Eliminar el proveedor
        proveedores.delete(id)
        
        # Devolver respuesta vacía
        # HTMX con outerHTML reemplazará la fila con nada (borrándola)
        return HttpResponse('')
    
    # Si no es POST, retornar error
    return render(request, "error.html", {
        'error': "Method not allowed. Use POST to delete."
    }, status=405)


def confirm_delete(request, id):
    """
    Renderiza modal de confirmación antes de eliminar.
    
    FLUJO:
    1. User hace click en "Eliminar" en tabla
    2. HTMX GET /agrosol/proveedores/confirm-delete/<id>/
    3. Esta función renderiza modal con variables:
       - delete_url: POST /agrosol/proveedores/eliminar/<id>/
       - table_body_id: #tabla-prov-body (para HTMX reemplace)
    
    VARIABLES ESPERADAS EN TEMPLATE:
    - row_id: ID del proveedor (para referencia)
    - delete_url: URL POST para eliminar
    - table_body_id: Selector CSS del contenedor a actualizar
    """
    return render(request, 'proveedores/confirm_delete.html#delete_proveedor', {
        'row_id': id,
        'delete_url': f"/agrosol/proveedores/eliminar/{id}/",  # ← POST a esta URL
        'table_body_id': '#tabla-prov-body'  # ← HTMX reemplaza este elemento
    })
