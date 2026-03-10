from django.shortcuts import render, redirect
from .services import api_client, proveedores
from .forms import *
from django.contrib.auth.decorators import login_required 

########## VISTAS DE EJEMPLO ##########ç
@login_required
def listar(request):
    cliente = api_client.get_all()
    print(cliente["data"])
    return render(request, "client/listar.html", {"cliente" : cliente["data"]})

@login_required
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

@login_required
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

@login_required
def eliminar(request, id):
    api_client.delete(id)
    return redirect("listar")

########## VISTAS DE PROVEEDORES ##########
@login_required
def list_proveedores(request):
    cliente = proveedores.get_all_proveedores()
    return render(request, "proveedores/index_proveedores.html", {'lista': cliente["data"]})

@login_required
def create_proveedor(request):
    if request.method == "POST":
        form = form_proveedores(request.POST or None, request.FILES or None)
        if form.is_valid():
            proveedores.create(form.cleaned_data)
            return redirect("proveedores")
    else:
        form = form_proveedores()
    return render(request, "proveedores/create_proveedor.html", {"form": form})

@login_required
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

@login_required
def delete_proveedor(request, id):
    proveedores.delete(id)
    return redirect("proveedores")

### Vista de prueba para login ###
@login_required
def principio (request):
    return render(request, "login/principio.html")

@login_required
def perfil(request):
    if request.method == "POST":
        # Datos del User
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()

        # Datos del perfil extendido
        perfil = request.user.profile
        perfil.cargo = request.POST.get('cargo', '')
        perfil.area = request.POST.get('area', '')
        perfil.telefono = request.POST.get('telefono', '')
        if 'avatar' in request.FILES:
            perfil.avatar = request.FILES['avatar']
        perfil.save()

        return redirect('perfil')

    return render(request, "login/principio.html")
