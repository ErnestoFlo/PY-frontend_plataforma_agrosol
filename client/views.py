from django.shortcuts import render, redirect
from .services import proveedores
from .forms import ProveedoresForm
from .utils import get_proveedores_for_table, build_menu_items

########## VISTAS POR DISEÑO ###########

def welcome(request):
    return render(request, "layouts/welcome.html", {
        "pagename": "Bienvenida",
        "menu_items": build_menu_items("Bienvenida"),
    })

def login(request):
    return render(request, "layouts/login.html", {
        "pagename": "Inicio de Sesión",
        "menu_items": build_menu_items("Inicio de Sesión"),
    })

def view1(request):
    return render(request, "design/view1.html", {
        "pagename": "Dashboard",
        "menu_items": build_menu_items("Dashboard"),
    })

def tests_form(request):
    return render(request, "design/main_form_test.html", {
        "pagename": "Main Form Test",
        "menu_items": build_menu_items("Main Form Test"),
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
        'menu_items': build_menu_items('Test & Views'),
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
    """
    Lista todos los proveedores con paginación.
    
    GET requests:
    - Retorna página HTML completa si es navegación normal
    - Retorna solo filas de tabla si es HTMX request (paginación)
    
    ANTES: 45 líneas de lógica repetida
    DESPUÉS: 15 líneas usando helpers
    """
    proveedores_data = proveedores.get_all_proveedores()
    page = int(request.GET.get('page', 1))
    
    # Usar helper que combina: extracción datos + transformación + paginación
    table_context = get_proveedores_for_table(proveedores_data, page)

    # Si es request HTMX (paginación sin recargar página)
    if request.headers.get('HX-Request'):
        return render(request, 'partials/tables.html#table_rows', {
            **table_context,
            'with_actions': True,
        })

    # Si es GET normal, retorna página completa
    return render(request, "proveedores/index_proveedores.html", {
        **table_context,
        'create_url': '/agrosol/proveedores/crear/',
        'pagename': 'Proveedores',
        'columns': ['Proveedor', 'Dirección', 'Contacto', 'Cargo', 'Teléfono', 'Celular', 'Email', 'Términos de Pago'],
        'table_body_id': '#tabla-prov-body',
        'menu_items': build_menu_items('Proveedores'),  # ← Pasar menú
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
            # La lógica cambia aquí: CREATE o UPDATE
            if id:
                proveedores.update(id, form.cleaned_data)  # PUT /api/Proveedores/<id>
            else:
                proveedores.create(form.cleaned_data)      # POST /api/Proveedores
            
            # Después de crear/editar, retornar tabla actualizada (flujo HTMX)
            proveedores_data = proveedores.get_all_proveedores()
            page = int(request.GET.get('page', 1))
            table_context = get_proveedores_for_table(proveedores_data, page)
            
            return render(request, "partials/tables.html#table_rows", {
                **table_context,
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
    return render(request, template, context)

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
        
        # Obtener lista actualizada y retornar tabla
        proveedores_data = proveedores.get_all_proveedores()
        page = int(request.GET.get('page', 1))
        table_context = get_proveedores_for_table(proveedores_data, page)
        
        return render(request, "partials/tables.html#table_rows", {
            **table_context,
            'with_actions': True,
        })
    
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
