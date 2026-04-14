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
            'delete_url': f"{PROVEEDOR_BASE_URL}/confirmar/{item_id}"
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
MENU_ITEMS_CONFIG = [
    {'url': 'test_form_page', 'icon': 'icon-image-regular', 'label': 'Pruebas formulario', 'page_name': 'Main Form Test'},
    {'url': 'tests_page', 'icon': 'icon-date-regular', 'label': 'Componentes', 'page_name': 'Test & Views'},
    {'url': 'dashboard', 'icon': 'icon-file-regular', 'label': 'Dashboard', 'page_name': 'Dashboard'},
    {'url': 'proveedores', 'icon': 'icon-pencil-regular', 'label': 'Proveedores', 'page_name': 'Proveedores'},
]


def build_menu_items(current_page_name: str) -> List[Dict[str, Any]]:
    menu_items = []
    
    for item in MENU_ITEMS_CONFIG:
        menu_items.append({
            'url': item['url'],
            'icon': item['icon'],
            'label': item['label'],
            'is_active': item['page_name'] == current_page_name,  # ← Determina si es activo
        })
    
    return menu_items
