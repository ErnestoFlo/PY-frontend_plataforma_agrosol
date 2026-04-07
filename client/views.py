from django.shortcuts import render, redirect
from .services import api_client, proveedores
from .forms import *

########## VISTAS POR DISEÑO ###########
# test_logs = [
#     {'initials': 'JG', 'user': 'Juan García', 'action': 'creó un nuevo proveedor', 'time': 'hace 2 min', 'hash': 'a3f9b2c', 'badge_variant': 'success', 'badge_text': 'Creado'},
#     {'initials': 'MA', 'user': 'María Alvarado', 'action': 'editó el proveedor Semillas del Sur', 'time': 'hace 15 min', 'hash': 'd1e8f3a', 'badge_variant': 'warning', 'badge_text': 'Editado'},
#     {'initials': 'RC', 'user': 'Roberto Castillo', 'action': 'eliminó el producto Fertilizante X', 'time': 'hace 1 hora', 'hash': 'b7c2d9e', 'badge_variant': 'danger', 'badge_text': 'Eliminado'},
#     {'initials': 'JG', 'user': 'Juan García', 'action': 'importó 24 registros desde Excel', 'time': 'hace 3 horas', 'hash': 'f4a1b8c', 'badge_variant': 'info', 'badge_text': 'Importado'},
#     {'initials': 'MA', 'user': 'María Alvarado', 'action': 'generó reporte mensual', 'time': 'ayer 5:30 PM', 'hash': 'e9d3c7f', 'badge_variant': None, 'badge_text': None},
# ]
def welcome(request):
    return render(request, "layouts/welcome.html", {"pagename": "Bienvenida"})

def login(request):
    return render(request, "layouts/login.html", {"pagename": "Inicio de Sesión"})

def view1(request):
    return render(request, "design/view1.html", {"pagename": "Dashboard"})

def tests_form(request):
    return render(request, "design/main_form_test.html", {"pagename": "Main Form Test"})

def tests_views(request):
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

    return render(request, 'design/components_tests&views.html', {
        'rows': paginated,
        'columns': ['Avatar', 'Header', 'Long Text Column', 'Header'],
        'current_page': page,
        'total_pages': total_pages,
        'page_range': range(1, total_pages + 1),
    })

def get_options(request):
    options = [
        {'id': 1,
        'nombre': 'Opcion 1'},
        {'id': 2,
        'nombre': 'Opcion 2'},
        {'id': 3,
        'nombre': 'Opcion 3'},
        {'id': 4,
        'nombre': 'Opcion 4'},
        {'id': 5,
        'nombre': 'Opcion 5'}
    ]
    return render(request, 'partials/options_lists.html#combobox_options', {'options': [{'value': o['id'], 'label': o['nombre']} for o in options]})

########## VISTAS DE EJEMPLO ##########
def listar(request):
    cliente = api_client.get_all()
    print(cliente["data"])
    return render(request, "client/listar.html", {"cliente" : cliente["data"]})

def crear(request):
    if request.method == "POST":
        data = {
            "proveedor": request.POST["proveedor"],
            "direccion": request.POST["direccion"],
            "contacto": request.POST["contacto"],
            "cargo": request.POST["cargo"],
            "telefono": request.POST["telefono"],
            "celular": request.POST["celular"],
            "email": request.POST["email"],
            "terminos_de_pago": request.POST["terminos_de_pago"],
        }
        api_client.create(data)
        return redirect("listar")
    
    return render(request, "client/form.html")

def editar(request, id):
    if request.method == "POST":
        data = {
            "proveedor": request.POST["proveedor"],
            "direccion": request.POST["direccion"],
            "contacto": request.POST["contacto"],
            "cargo": request.POST["cargo"],
            "telefono": request.POST["telefono"],
            "celular": request.POST["celular"],
            "email": request.POST["email"],
            "terminos_de_pago": request.POST["terminos_de_pago"],
        }
        api_client.update(id, data)
        return redirect("listar")
    
    cliente = api_client.get_by_id(id)
    return render(request, "client/form.html", {"cliente": cliente})

def eliminar(request, id):
    api_client.delete(id)
    return redirect("listar")

########## VISTAS DE PROVEEDORES ##########
def list_proveedores(request):
    cliente = proveedores.get_all_proveedores()
    return render(request, "proveedores/index_proveedores.html", {'lista': cliente["data"]})

def create_proveedor(request):
    if request.method == "POST":
        form = form_proveedores(request.POST or None, request.FILES or None)
        if form.is_valid():
            proveedores.create(form.cleaned_data)
            return redirect("proveedores")
    else:
        form = form_proveedores()
    return render(request, "proveedores/create_proveedor.html", {"form": form})

def edit_proveedor(request, id):
    form = None
    if request.method == "POST":
        form = form_proveedores(request.POST or None, request.FILES or None)
        if form.is_valid():
            proveedores.update(id, form.cleaned_data)
            return redirect("proveedores")
    else:
        cliente = proveedores.get_by_id(id)
        form = form_proveedores(initial=cliente["data"])

    return render(request, "proveedores/edit_proveedor.html", {"form": form})

def delete_proveedor(request, id):
    proveedores.delete(id)
    return redirect("proveedores")
