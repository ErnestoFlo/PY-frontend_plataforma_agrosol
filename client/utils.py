from typing import Dict, List, Any, Tuple


# ============================================================================
# CONFIG
# ============================================================================

PROVEEDOR_ID_FIELD = 'proveedoresID'
PROVEEDOR_CELL_FIELDS = [
    'proveedor', 
    'direccion', 
    'contacto', 
    'cargo', 
    'telefono', 
    'celular', 
    'email', 
    'terminos_de_pago'
]
PROVEEDOR_PER_PAGE = 100
PROVEEDOR_BASE_URL = '/agrosol/proveedores'

PROVEEDOR_COLUMNS_CONFIG = [
    {'label': 'proveedor', 'visibility': 'always', 'priority': 1},
    {'label': 'direccion', 'visibility': 'lg', 'priority': 3},
    {'label': 'contacto', 'visibility': 'always', 'priority': 2},
    {'label': 'cargo', 'visibility': 'xl', 'priority': 4},
    {'label': 'teléfono', 'visibility': 'always', 'priority': 5},
    {'label': 'celular', 'visibility': 'xl', 'priority': 6},
    {'label': 'email', 'visibility': 'lg', 'priority': 7},
    {'label': 'terminos_de_pago', 'visibility': 'xl', 'priority': 8},
]

# ============================================================================
# HELPERS
# ============================================================================

def extract_api_data(api_response: Dict[str, Any]) -> List[Dict]:
    if isinstance(api_response, dict):
        return api_response.get("data", [])
    elif isinstance(api_response, list):
        return api_response
    return []


def get_item_id(item: Dict[str, Any]) -> str:
    return item.get(PROVEEDOR_ID_FIELD) or item.get('id')


def build_table_rows(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for item in items:
        item_id = get_item_id(item)
        row = {
            'id': item_id,
            'cells': [item.get(field, '') for field in PROVEEDOR_CELL_FIELDS],
            'edit_url': f"{PROVEEDOR_BASE_URL}/editar/{item_id}",
            'delete_url': f"{PROVEEDOR_BASE_URL}/confirmar/{item_id}",
            'actions_id': f"actions-{item_id}"
        }
        rows.append(row)
    return rows


def paginate(items: List[Dict[str, Any]], page: int, per_page: int = PROVEEDOR_PER_PAGE) -> Tuple[List[Dict], int, int, range]:
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
    
    return paginated, total_pages, page, range(1, total_pages + 1)


def get_paginated_table_data(items: List[Dict[str, Any]], page: int) -> Dict[str, Any]:
    paginated, total_pages, current_page, page_range = paginate(items, page)
    
    return {
        'columns': PROVEEDOR_COLUMNS_CONFIG,
        'rows': paginated,
        'total_pages': total_pages,
        'current_page': current_page,
        'page_range': page_range,
    }


# ============================================================================
# COMPOSITE HELPERS - Llujo completo de data
# ============================================================================

def get_proveedores_for_table(api_response: Dict[str, Any], page: int) -> Dict[str, Any]:
    rows_raw = extract_api_data(api_response)
    rows = build_table_rows(rows_raw)
    return get_paginated_table_data(rows, page)


# ============================================================================
# MENU - Gestión del menú lateral
# ============================================================================

# Definición centralizada de items del menú
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