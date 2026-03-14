from django.shortcuts import render, redirect
from .services import api_client, proveedores
from .forms import *
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404


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
    return render(request, "usuarios/principio.html")

########## USUARIOS ##########
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

    return render(request, "usuarios/principio.html")

# ── Decorador reutilizable para superusuarios ──
def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            raise PermissionDenied  # → 403
        return view_func(request, *args, **kwargs)
    return wrapper


# ── LISTADO DE USUARIOS ──
@superuser_required
def lista_usuarios(request):
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,
        'total': usuarios.count(),
        'activos': usuarios.filter(is_active=True).count(),
        'staff': usuarios.filter(is_staff=True).count(),
        'superusers': usuarios.filter(is_superuser=True).count(),
    })


# ── EDITAR USUARIO ──
@superuser_required
def editar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)

    # Evitar que se edite a sí mismo desde aquí
    if usuario == request.user:
        return redirect('lista_usuarios')

    if request.method == "POST":
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name  = request.POST.get('last_name', '')
        usuario.email = request.POST.get('email', '')
        usuario.is_staff = 'is_staff'      in request.POST
        usuario.is_superuser = 'is_superuser'  in request.POST
        usuario.save()

        # Datos del perfil extendido
        usuario.profile.cargo = request.POST.get('cargo', '')
        usuario.profile.area = request.POST.get('area', '')
        usuario.profile.telefono = request.POST.get('telefono', '')
        usuario.profile.save()

        return redirect('lista_usuarios')

    return render(request, 'usuarios/editar.html', {
        'usuario': usuario
    })


# ── DESACTIVAR USUARIO (soft delete) ──
@superuser_required
def desactivar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)

    # Protecciones importantes
    if usuario == request.user:
        return redirect('lista_usuarios')  # No puede desactivarse a sí mismo
    if usuario.is_superuser:
        return redirect('lista_usuarios')  # No puede desactivar a otro superusuario

    if request.method == "POST":
        usuario.is_active = False  # Soft delete — no borra, solo desactiva
        usuario.save()
        return redirect('lista_usuarios')

    return render(request, 'usuarios/confirmar_desactivar.html', {
        'usuario': usuario
    })

########## PÁGINA DE ERRORES ###########

def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)

from django.core.exceptions import SuspiciousOperation

def test_400(request):
    raise SuspiciousOperation("Prueba de error 400")