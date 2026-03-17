from .forms import *
from .services import api_client, proveedores
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Modulo, Componente, PermisoGrupo, get_permisos
import json


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

########## PERMISOS GRANULARES ###########

# ── Decorador reutilizable para superusuarios ───────────────
def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


# ════════════════════════════════════════════════════════════════
#  PANEL PRINCIPAL — Lista de grupos con sus módulos
# ════════════════════════════════════════════════════════════════
@superuser_required
def panel_permisos(request):
    grupos  = Group.objects.prefetch_related('permisos_granulares').all().order_by('name')
    modulos = Modulo.objects.filter(activo=True).prefetch_related('componentes')
    usuarios_sin_grupo = User.objects.filter(groups=None, is_active=True).exclude(is_superuser=True)

    return render(request, 'permisos/panel.html', {
        'grupos':              grupos,
        'modulos':             modulos,
        'usuarios_sin_grupo':  usuarios_sin_grupo,
        'total_grupos':        grupos.count(),
        'total_modulos':       modulos.count(),
        'total_componentes':   Componente.objects.filter(activo=True).count(),
    })


# ════════════════════════════════════════════════════════════════
#  CREAR GRUPO
# ════════════════════════════════════════════════════════════════
@superuser_required
@require_POST
def grupo_crear(request):
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'success': False, 'error': 'El nombre es requerido.'}, status=400)
    if Group.objects.filter(name=nombre).exists():
        return JsonResponse({'success': False, 'error': f'El grupo "{nombre}" ya existe.'}, status=400)

    grupo = Group.objects.create(name=nombre)
    return JsonResponse({
        'success': True,
        'grupo': {'id': grupo.id, 'name': grupo.name}
    })


# ════════════════════════════════════════════════════════════════
#  ELIMINAR GRUPO
# ════════════════════════════════════════════════════════════════
@superuser_required
@require_POST
def grupo_eliminar(request, id):
    grupo = get_object_or_404(Group, id=id)
    nombre = grupo.name
    grupo.delete()
    return JsonResponse({'success': True, 'nombre': nombre})


# ════════════════════════════════════════════════════════════════
#  EDITOR DE PERMISOS DE UN GRUPO
#  Muestra todos los módulos y componentes con toggles
# ════════════════════════════════════════════════════════════════
@superuser_required
def grupo_editar_permisos(request, id):
    grupo   = get_object_or_404(Group, id=id)
    modulos = Modulo.objects.filter(activo=True).prefetch_related('componentes')

    # Construir estructura de permisos actuales del grupo
    permisos_actuales = {}
    for perm in PermisoGrupo.objects.filter(group=grupo).select_related('componente'):
        permisos_actuales[perm.componente.id] = {
            'ver':  perm.puede_ver,
            'usar': perm.puede_usar,
        }

    # Usuarios asignados a este grupo
    usuarios_del_grupo = grupo.user_set.filter(is_active=True).select_related('profile')
    # Usuarios disponibles para asignar
    usuarios_disponibles = User.objects.filter(
        is_active=True, is_superuser=False
    ).exclude(groups=grupo).select_related('profile')

    return render(request, 'permisos/editar_grupo.html', {
        'grupo':                grupo,
        'modulos':              modulos,
        'permisos_actuales':    permisos_actuales,
        'usuarios_del_grupo':   usuarios_del_grupo,
        'usuarios_disponibles': usuarios_disponibles,
    })


# ════════════════════════════════════════════════════════════════
#  GUARDAR PERMISOS DE UN GRUPO (AJAX)
#  Recibe JSON: { componente_id: { ver: bool, usar: bool }, ... }
# ════════════════════════════════════════════════════════════════
@superuser_required
@require_POST
def grupo_guardar_permisos(request, id):
    grupo = get_object_or_404(Group, id=id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

    # Procesar cada componente enviado
    actualizados = 0
    for comp_id_str, perms in data.items():
        try:
            comp_id = int(comp_id_str)
            comp    = Componente.objects.get(id=comp_id)
        except (ValueError, Componente.DoesNotExist):
            continue

        PermisoGrupo.objects.update_or_create(
            group=grupo,
            componente=comp,
            defaults={
                'puede_ver':  perms.get('ver',  False),
                'puede_usar': perms.get('usar', False),
            }
        )
        actualizados += 1

    return JsonResponse({
        'success':     True,
        'actualizados': actualizados,
        'grupo':       grupo.name,
    })


# ════════════════════════════════════════════════════════════════
#  ASIGNAR USUARIO A GRUPO (AJAX)
# ════════════════════════════════════════════════════════════════
@superuser_required
@require_POST
def grupo_asignar_usuario(request, id):
    grupo    = get_object_or_404(Group, id=id)
    user_id  = request.POST.get('user_id')
    accion   = request.POST.get('accion', 'agregar')  # 'agregar' o 'quitar'

    try:
        usuario = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'}, status=404)

    if accion == 'agregar':
        usuario.groups.add(grupo)
        msg = f'{usuario.username} agregado al grupo {grupo.name}'
    else:
        usuario.groups.remove(grupo)
        msg = f'{usuario.username} removido del grupo {grupo.name}'

    return JsonResponse({
        'success': True,
        'mensaje': msg,
        'usuario': {
            'id':       usuario.id,
            'username': usuario.username,
            'nombre':   usuario.get_full_name() or usuario.username,
        }
    })


# ════════════════════════════════════════════════════════════════
#  OBTENER PERMISOS DE UN GRUPO (para preview)
# ════════════════════════════════════════════════════════════════
@superuser_required
def grupo_preview_permisos(request, id):
    grupo   = get_object_or_404(Group, id=id)
    modulos = Modulo.objects.filter(activo=True).prefetch_related('componentes')

    resumen = []
    for modulo in modulos:
        componentes_info = []
        for comp in modulo.componentes.filter(activo=True):
            try:
                perm = PermisoGrupo.objects.get(group=grupo, componente=comp)
                ver  = perm.puede_ver
                usar = perm.puede_usar
            except PermisoGrupo.DoesNotExist:
                ver = usar = False
            componentes_info.append({
                'nombre': comp.nombre,
                'clave':  comp.clave,
                'tipo':   comp.tipo,
                'ver':    ver,
                'usar':   usar,
            })
        resumen.append({
            'modulo':       modulo.nombre,
            'componentes':  componentes_info,
        })

    return JsonResponse({'success': True, 'grupo': grupo.name, 'resumen': resumen})

@login_required
def prueba_tecnica(request):
    return render(request, 'permisos/prueba_tecnica.html')