"""Helpers de presentación para vistas server-rendered + HTMX.

Este módulo concentra:
- transformación de payloads API a filas de UI reutilizables
- paginación consistente para desktop/mobile
- configuración de menú para sidebar/mobilebar
"""

from typing import Dict, List, Any, Tuple, Union
# ============================================================================
# CONFIG
# ============================================================================
# Punto de extensión principal para nuevos módulos CRUD basados en tabla.
# Agregar aquí un nuevo modelo evita condicionales dispersos en vistas/templates.
MODELS_CONFIG = {
    'PER_PAGE': 25,
    'proveedores': {
        'id_field': 'proveedoresID',
        'cell_fields': [
            'proveedor', 
            'direccion', 
            'contacto', 
            'cargo', 
            'telefono', 
            'celular', 
            'email', 
            'terminos_de_pago'
        ],
        'card_fields': [
            'proveedor',
            'contacto',
            'telefono',
            'celular',
        ],
        'base_url': '/agrosol/proveedores',
    },
}

# ============================================================================
# HELPERS
# ============================================================================

def extract_api_data(api_response: Dict[str, Any]) -> List[Dict]:
    """Normaliza respuestas API heterogéneas a una lista de items."""
    if isinstance(api_response, dict):
        return api_response.get("data", [])
    elif isinstance(api_response, list):
        return api_response
    return []

def get_item_id(item: Dict[str, Any], model: str) -> str:
    """Obtiene el ID de un item con fallback genérico."""
    return item.get(MODELS_CONFIG[model]['id_field']) or item.get('id')

def build_table_rows(items: List[Dict[str, Any]], model: str) -> List[Dict[str, Any]]:
    """Construye el contrato que consumen `partials/tables.html` y cards mobile.

    Campos clave del contrato:
    - id / cells / prior_cols / id_col
    - edit_url / delete_url / detail_url
    - actions_id (ID único del popover por fila)
    """
    rows = []
    for item in items:
        item_id = get_item_id(item, model)
        cells = dict(zip(
                MODELS_CONFIG[model]['cell_fields'],
                [item.get(field, '') for field in MODELS_CONFIG[model]['cell_fields']]))
        prior_cols = {k: cells.get(k, '') for k in MODELS_CONFIG[model]['card_fields']}
        row = {
            'id': item_id,
            'cells': cells,
            'prior_cols': prior_cols,
            'id_col': cells.get(MODELS_CONFIG[model]['card_fields'][0], ''),
            'edit_url': f"{MODELS_CONFIG[model]['base_url']}/editar/{item_id}",
            'delete_url': f"{MODELS_CONFIG[model]['base_url']}/confirmar/{item_id}",
            'detail_url': f"{MODELS_CONFIG[model]['base_url']}/?id={item_id}&detail=true&viewport=mobile",
            'actions_id': f"actions-{item_id}",
        }
        rows.append(row)
    return rows

def build_pagination_window(current_page: int, total_pages: int, window: int = 2) -> List[Union[int, str]]:
    """Genera la ventana de paginación con elipsis para tablas HTMX."""
    if total_pages <= 1:
        return [1]

    pages = set([1, total_pages])
    start = max(1, current_page - window)
    end = min(total_pages, current_page + window)

    for page in range(start, end + 1):
        pages.add(page)

    sorted_pages = sorted(pages)
    result: List[Union[int, str]] = []
    previous = None
    for page in sorted_pages:
        if previous is not None and page - previous > 1:
            result.append('ellipsis')
        result.append(page)
        previous = page
    return result

def paginate(items: List[Dict[str, Any]], page: int, per_page: int = MODELS_CONFIG['PER_PAGE']) -> Tuple[List[Dict], int, int]:
    """Pagina una lista en memoria y corrige páginas fuera de rango."""
    if page < 1:
        page = 1
        
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    # Validar que page no exceda total_pages
    if page > total_pages:
        page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated = items[start:end]
    
    return paginated, total_pages, page

def get_paginated_table_data(items: List[Dict[str, Any]], page: int) -> Dict[str, Any]:
    """Empaqueta filas paginadas + metadatos para `tables.html`."""
    paginated, total_pages, current_page = paginate(items, page)
    
    return {
        'rows': paginated,
        'total_pages': total_pages,
        'current_page': current_page,
        'page_items': build_pagination_window(current_page, total_pages),
    }

# ============================================================================
# COMPOSITE HELPERS - Flujo completo de data
# ============================================================================

def get_data_for_table(api_response: Dict[str, Any], page: int, model: str) -> Dict[str, Any]:
    """Pipeline completo: API response -> rows UI -> paginación."""
    rows_raw = extract_api_data(api_response)
    rows = build_table_rows(rows_raw, model)
    return get_paginated_table_data(rows, page)

# ============================================================================
# MENU - Gestión del menú lateral
# ============================================================================

# Definición centralizada de items del menú.
# `page_name` determina qué item se renderiza como activo.
MENU_SIDEBAR_ITEMS_CONFIG = [
    {'url': 'dashboard', 'icon': 'icon-home', 'label': 'Inicio', 'page_name': 'Dashboard', 'group': []},
    {'url': '', 'icon': 'icon-products', 'label': 'Productos', 'page_name': '', 'group': [
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Maestro', 'page_name': 'Maestro de Productos', 'group': []},
        {'url': 'proveedores', 'icon': 'icon-provider', 'label': 'Proveedores', 'page_name': 'Proveedores', 'group': []},
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Marcas', 'page_name': 'Marcas', 'group': []},
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Líneas', 'page_name': 'Líneas', 'group': []},
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Categorías', 'page_name': 'Categorías', 'group': []},
    ]},
]
MENU_MOBILEBAR_ITEMS_CONFIG = [
    {'url': 'dashboard', 'icon': 'icon-home', 'label': 'Inicio', 'page_name': 'Dashboard', 'group': []},
    {'url': '', 'icon': 'icon-products', 'label': 'Productos', 'page_name': '', 'group': [
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Maestro', 'page_name': 'Maestro de Productos', 'group': []},
        {'url': 'proveedores', 'icon': 'icon-provider', 'label': 'Proveedores', 'page_name': 'Proveedores', 'group': []},
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Marcas', 'page_name': 'Marcas', 'group': []},
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Líneas', 'page_name': 'Líneas', 'group': []},
        {'url': 'dashboard', 'icon': 'icon-user-crown', 'label': 'Categorías', 'page_name': 'Categorías', 'group': []},
    ]},
]

def build_menu_sidebar_items(current_page_name: str) -> List[Dict[str, Any]]:
    """Entrega estructura lista para renderizar `components/sidebar.html`."""
    menu_items = []
    
    for item in MENU_SIDEBAR_ITEMS_CONFIG:
        if item['page_name'] == current_page_name:
            icon = f'{item['icon']}-fill'  # ← Icono activo
            active = True
        else:
            icon = f'{item['icon']}-regular'  # ← Icono inactivo,
            active = False
        group_items_copy = []
        for sub_item in item['group']:
            sub_item_copy = sub_item.copy()  # ← Copia shallow
            if sub_item_copy['page_name'] == current_page_name:
                sub_item_copy['icon'] = f"{sub_item_copy['icon']}-fill"
                sub_item_copy['is_active'] = True
            else:
                sub_item_copy['icon'] = f"{sub_item_copy['icon']}-regular"
                sub_item_copy['is_active'] = False
            group_items_copy.append(sub_item_copy)
        
        menu_items.append({
            'url': item['url'],
            'icon': icon,
            'label': item['label'],
            'is_active': active,
            'group': group_items_copy,
        })  
    return menu_items

def build_menu_mobilebar_items(current_page_name: str) -> List[Dict[str, Any]]:
    """Versión mobile del menú, con el mismo contrato visual del sidebar."""
    menu_items = []
    
    for item in MENU_MOBILEBAR_ITEMS_CONFIG:
        if item['page_name'] == current_page_name:
            icon = f'{item['icon']}-fill'  # ← Icono activo
            active = True
        else:
            icon = f'{item['icon']}-regular'  # ← Icono inactivo,
            active = False
        group_items_copy = []
        for sub_item in item['group']:
            sub_item_copy = sub_item.copy()  # ← Copia shallow
            if sub_item_copy['page_name'] == current_page_name:
                sub_item_copy['icon'] = f"{sub_item_copy['icon']}-fill"
                sub_item_copy['is_active'] = True
            else:
                sub_item_copy['icon'] = f"{sub_item_copy['icon']}-regular"
                sub_item_copy['is_active'] = False
            group_items_copy.append(sub_item_copy)
        
        menu_items.append({
            'url': item['url'],
            'icon': icon,
            'label': item['label'],
            'is_active': active,
            'group': group_items_copy,
        })  
    return menu_items