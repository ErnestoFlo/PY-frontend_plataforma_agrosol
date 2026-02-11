from django.shortcuts import render, redirect
from .services import api_client, proveedores
from .forms import *

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
