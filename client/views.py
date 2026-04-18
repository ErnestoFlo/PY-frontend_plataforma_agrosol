from .forms import *
from .services import api_client, proveedores
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Modulo, Componente, PermisoGrupo, get_permisos, AccesoModulo, tiene_acceso_modulo, escanear_template, PermisoElemento, Elemento, registrar_actividad
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
# ── PROVEEDORES ───────────────────────────────────────────────
 
@login_required
@registrar_actividad(accion='buscar', modelo='Proveedor', campo_busqueda='q')
def list_proveedores(request):
    cliente = proveedores.get_all_proveedores()
    return render(request, "proveedores/index_proveedores.html", {'lista': cliente["data"]})
 
 
@login_required
@registrar_actividad(accion='crear', modelo='Proveedor', campo_label='proveedor')
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
@registrar_actividad(accion='editar', modelo='Proveedor', campo_label='proveedor')
def edit_proveedor(request, id):
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
@registrar_actividad(accion='eliminar', modelo='Proveedor')
def delete_proveedor(request, id):
    proveedores.delete(id)
    return redirect("proveedores")
 
 
# ── CÓMO AGREGAR LOGS A CUALQUIER VISTA NUEVA ──────────────────────
#
# 1. CREAR registro:
#    @registrar_actividad(accion='crear', modelo='NombreModelo', campo_label='campo_nombre')
#
# 2. EDITAR registro:
#    @registrar_actividad(accion='editar', modelo='NombreModelo', campo_label='campo_nombre')
#
# 3. ELIMINAR registro:
#    @registrar_actividad(accion='eliminar', modelo='NombreModelo')
#    (no necesita campo_label porque no hay POST con datos del registro)
#
# 4. BUSCAR / CONSULTAR:
#    @registrar_actividad(accion='buscar', modelo='NombreModelo', campo_busqueda='q')
#    (campo_busqueda es el nombre del parámetro GET, default 'q')
#
# El decorador SIEMPRE va DESPUÉS de @login_required
# para garantizar que request.user está disponible.


### Vista de prueba para login ###
@login_required
def principio (request):
    return render(request, "usuarios/principio.html")

########## USUARIOS ##########
# @login_required
# def perfil(request):
#     if request.method == "POST":
#         # Datos del User
#         request.user.first_name = request.POST.get('first_name', '')
#         request.user.last_name = request.POST.get('last_name', '')
#         request.user.email = request.POST.get('email', '')
#         request.user.save()

#         # Datos del perfil extendido
#         perfil = request.user.profile
#         perfil.cargo = request.POST.get('cargo', '')
#         perfil.area = request.POST.get('area', '')
#         perfil.telefono = request.POST.get('telefono', '')
#         if 'avatar' in request.FILES:
#             perfil.avatar = request.FILES['avatar']
#         perfil.save()

#         return redirect('perfil')

#     return render(request, "usuarios/principio.html")

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
    grupos   = Group.objects.all().order_by('name')  # ← necesario para el select del modal
    return render(request, 'usuarios/lista.html', {
        'usuarios':   usuarios,
        'grupos':     grupos,             # ← pasar grupos al template
        'total':      usuarios.count(),
        'activos':    usuarios.filter(is_active=True).count(),
        'staff':      usuarios.filter(is_staff=True).count(),
        'superusers': usuarios.filter(is_superuser=True).count(),
    })

@superuser_required
@require_POST
def crear_usuario(request):
    """
    Crea un nuevo usuario desde el modal de la lista de usuarios.
    Recibe multipart/form-data (para poder incluir avatar).
    Retorna JSON.
    """
    username     = request.POST.get('username', '').strip()
    first_name   = request.POST.get('first_name', '').strip()
    last_name    = request.POST.get('last_name', '').strip()
    email        = request.POST.get('email', '').strip()
    password1    = request.POST.get('password1', '')
    password2    = request.POST.get('password2', '')
    cargo        = request.POST.get('cargo', '').strip()
    area         = request.POST.get('area', '').strip()
    telefono     = request.POST.get('telefono', '').strip()
    is_staff     = request.POST.get('is_staff',     '0') == '1'
    is_superuser = request.POST.get('is_superuser', '0') == '1'
    grupo_id     = request.POST.get('grupo', '').strip()
 
    # ── Validaciones ──
    if not username:
        return JsonResponse({'success': False, 'error': 'El username es obligatorio.'}, status=400)
 
    if User.objects.filter(username=username).exists():
        return JsonResponse({'success': False, 'error': f'El username "{username}" ya está en uso.'}, status=400)
 
    if not password1:
        return JsonResponse({'success': False, 'error': 'La contraseña es obligatoria.'}, status=400)
 
    if len(password1) < 8:
        return JsonResponse({'success': False, 'error': 'La contraseña debe tener mínimo 8 caracteres.'}, status=400)
 
    if password1 != password2:
        return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden.'}, status=400)
 
    if email and User.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'error': f'El email "{email}" ya está en uso.'}, status=400)
 
    # ── Crear el User ──
    usuario = User.objects.create_user(
        username=username,
        password=password1,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    usuario.is_staff     = is_staff
    usuario.is_superuser = is_superuser
    usuario.save()
 
    # ── Actualizar perfil extendido ──
    perfil = usuario.profile  # se crea automáticamente con la signal
    perfil.cargo    = cargo
    perfil.area     = area
    perfil.telefono = telefono
    if 'avatar' in request.FILES:
        perfil.avatar = request.FILES['avatar']
    perfil.save()
 
    # ── Asignar grupo ──
    if grupo_id:
        try:
            grupo = Group.objects.get(id=int(grupo_id))
            usuario.groups.add(grupo)
        except (Group.DoesNotExist, ValueError):
            pass  # Si el grupo no existe, simplemente no se asigna
 
    # ── Preparar respuesta ──
    avatar_url = None
    if perfil.avatar and perfil.avatar.name:
        avatar_url = perfil.avatar.url
 
    return JsonResponse({
        'success': True,
        'usuario': {
            'id':          usuario.id,
            'username':    usuario.username,
            'first_name':  usuario.first_name,
            'last_name':   usuario.last_name,
            'full_name':   usuario.get_full_name() or usuario.username,
            'email':       usuario.email,
            'cargo':       perfil.cargo,
            'area':        perfil.area,
            'is_staff':    usuario.is_staff,
            'is_superuser':usuario.is_superuser,
            'avatar_url':  avatar_url,
            'date_joined': usuario.date_joined.strftime('%d/%m/%Y'),
        }
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


# ══════════════════════════════════════════════════════════════
#  VISTAS A AGREGAR/REEMPLAZAR en client/views.py
# ══════════════════════════════════════════════════════════════

# 1. Reemplaza panel_permisos
@superuser_required
def panel_permisos(request):
    from django.contrib.auth.models import Group
    grupos  = Group.objects.all().order_by('name').prefetch_related(
        'user_set', 'accesos_modulos__modulo'
    )
    modulos = Modulo.objects.filter(activo=True).prefetch_related('accesos__group')
    usuarios_activos = User.objects.filter(
        is_active=True, is_superuser=False
    ).order_by('first_name','username').select_related('profile').prefetch_related('groups')

    usuarios_con_grupo = usuarios_activos.filter(groups__isnull=False).distinct()
    usuarios_sin_grupo = usuarios_activos.filter(groups=None)

    return render(request, 'permisos/panel.html', {
        'grupos':           grupos,
        'modulos':          modulos,
        'todos_usuarios':   usuarios_activos,
        'lista_sin_grupo':  usuarios_sin_grupo,
        'total_grupos':     grupos.count(),
        'total_modulos':    modulos.count(),
        'total_usuarios':   usuarios_activos.count(),
        'usuarios_sin_grupo':  usuarios_sin_grupo.count(),
        'usuarios_asignados':  usuarios_con_grupo.count(),
    })


# 2. Agregar modulo_crear
@superuser_required
@require_POST
def modulo_crear(request):
    from django.utils.text import slugify
    nombre   = request.POST.get('nombre','').strip()
    icono    = request.POST.get('icono','bi-grid').strip()
    url_name = request.POST.get('url_name','').strip()
    desc     = request.POST.get('descripcion','').strip()

    if not nombre:
        return JsonResponse({'success':False,'error':'El nombre es requerido.'},status=400)

    slug = slugify(nombre)
    if Modulo.objects.filter(slug=slug).exists():
        return JsonResponse({'success':False,'error':'Ya existe un módulo con ese nombre.'},status=400)

    m = Modulo.objects.create(
        nombre=nombre, slug=slug, icono=icono,
        url_name=url_name, descripcion=desc,
        orden=Modulo.objects.count()+1
    )
    return JsonResponse({'success':True,'modulo':{
        'id':m.id,'nombre':m.nombre,'slug':m.slug,
        'icono':m.icono,'url_name':m.url_name,'descripcion':m.descripcion,
    }})


# 3. Agregar modulo_eliminar
@superuser_required
@require_POST
def modulo_eliminar(request, id):
    modulo = get_object_or_404(Modulo, id=id)
    nombre = modulo.nombre
    modulo.delete()
    return JsonResponse({'success':True,'nombre':nombre})


# 4. Agregar grupo_gestionar_modulo (asignar/revocar acceso)
@superuser_required
@require_POST
def grupo_gestionar_modulo(request, id):
    from django.contrib.auth.models import Group
    grupo    = get_object_or_404(Group, id=id)
    modulo_id = request.POST.get('modulo_id','').strip()
    accion    = request.POST.get('accion','asignar')

    modulo = get_object_or_404(Modulo, id=modulo_id)

    if accion == 'asignar':
        AccesoModulo.objects.update_or_create(
            group=grupo, modulo=modulo,
            defaults={'tiene_acceso': True}
        )
        msg = f'Acceso a "{modulo.nombre}" concedido a {grupo.name}'
    else:
        AccesoModulo.objects.filter(group=grupo, modulo=modulo).delete()
        msg = f'Acceso a "{modulo.nombre}" revocado de {grupo.name}'

    return JsonResponse({
        'success':     True,
        'mensaje':     msg,
        'modulo_icono': modulo.icono,
    })

@superuser_required
@require_POST
def modulo_editar(request, id):
    from django.utils.text import slugify
    modulo = get_object_or_404(Modulo, id=id)
 
    nombre   = request.POST.get('nombre',      '').strip()
    icono    = request.POST.get('icono',        modulo.icono).strip()
    url_name = request.POST.get('url_name',     '').strip()
    desc     = request.POST.get('descripcion',  '').strip()
 
    if not nombre:
        return JsonResponse({'success': False, 'error': 'El nombre es requerido.'}, status=400)
 
    # Verificar que el nuevo nombre no colisione con otro módulo
    nuevo_slug = slugify(nombre)
    if Modulo.objects.filter(slug=nuevo_slug).exclude(id=id).exists():
        return JsonResponse({'success': False, 'error': 'Ya existe un módulo con ese nombre.'}, status=400)
 
    modulo.nombre      = nombre
    modulo.slug        = nuevo_slug
    modulo.icono       = icono or 'bi-grid'
    modulo.url_name    = url_name
    modulo.descripcion = desc
    modulo.save()
 
    return JsonResponse({
        'success': True,
        'modulo': {
            'id':          modulo.id,
            'nombre':      modulo.nombre,
            'slug':        modulo.slug,
            'icono':       modulo.icono,
            'url_name':    modulo.url_name,
            'descripcion': modulo.descripcion,
        }
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
    grupo   = get_object_or_404(Group, id=id)
    user_id = request.POST.get('user_id')
    accion  = request.POST.get('accion', 'agregar')
 
    try:
        usuario = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'}, status=404)
 
    if accion == 'agregar':
        # ── Regla: un usuario solo puede pertenecer a UN grupo ──
        grupo_anterior = usuario.groups.first()
        usuario.groups.clear()   # quita cualquier grupo previo
        usuario.groups.add(grupo)
        msg = f'{usuario.username} asignado a {grupo.name}'
        return JsonResponse({
            'success': True,
            'mensaje': msg,
            'grupo_anterior': grupo_anterior.name if grupo_anterior and grupo_anterior.id != grupo.id else None,
            'usuario': {
                'id':       usuario.id,
                'username': usuario.username,
                'nombre':   usuario.get_full_name() or usuario.username,
            }
        })
    else:
        usuario.groups.remove(grupo)
        msg = f'{usuario.username} removido de {grupo.name}'
        return JsonResponse({'success': True, 'mensaje': msg, 'usuario': {
            'id': usuario.id, 'username': usuario.username,
            'nombre': usuario.get_full_name() or usuario.username,
        }})


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

########## Prueba tecnica ##########
@login_required
def prueba_tecnica(request):
    if not tiene_acceso_modulo(request.user, 'prueba_tecnica'):
        raise PermissionDenied
    
    permisos = get_permisos(request.user, 'prueba_tecnica')
    return render(request, 'permisos/prueba_tecnica.html', {'permisos': permisos})

##### Control de elementos ######

@superuser_required
@require_POST
def modulo_escanear(request, id):
    # Escanea el template del módulo y registra automáticamente
    # todos los elementos con data-permiso que encuentre.

    modulo = get_object_or_404(Modulo, id=id)
    resultado = escanear_template(modulo)
 
    if 'error' in resultado:
        return JsonResponse({'success': False, 'error': resultado['error']}, status=400)
 
    return JsonResponse({
        'success':    True,
        'modulo':     modulo.nombre,
        'creados':    resultado['creados'],
        'existentes': resultado['existentes'],
        'total':      resultado['total'],
        'elementos':  [
            {
                'id':    e.id,
                'clave': e.clave,
                'tipo':  e.tipo,
                'label': e.label,
            }
            for e in modulo.elementos.filter(activo=True).order_by('tipo', 'orden')
        ],
    })
 
 
@superuser_required
def modulo_elementos(request, id):
    # Retorna los elementos de un módulo (para el panel de permisos).
    # GET: devuelve elementos con los permisos del grupo indicado.

    modulo   = get_object_or_404(Modulo, id=id)
    grupo_id = request.GET.get('grupo_id')
 
    elementos = modulo.elementos.filter(activo=True).order_by('tipo', 'orden')
 
    data = []
    for elem in elementos:
        perm_data = {'ver': True, 'usar': True}  # default
 
        if grupo_id:
            try:
                grupo = Group.objects.get(id=grupo_id)
                perm  = PermisoElemento.objects.filter(
                    group=grupo, elemento=elem
                ).first()
                if perm:
                    perm_data = {'ver': perm.puede_ver, 'usar': perm.puede_usar}
            except Group.DoesNotExist:
                pass
 
        data.append({
            'id':    elem.id,
            'clave': elem.clave,
            'tipo':  elem.tipo,
            'label': elem.label,
            'ver':   perm_data['ver'],
            'usar':  perm_data['usar'],
        })
 
    return JsonResponse({
        'success':  True,
        'modulo':   {'id': modulo.id, 'nombre': modulo.nombre},
        'elementos': data,
    })
 
 
@superuser_required
@require_POST
def grupo_guardar_permisos_elemento(request, grupo_id, elemento_id):
    # Guarda el permiso ver/usar de un elemento específico para un grupo.
    # Llamado por el toggle en el panel — una petición por toggle.

    grupo    = get_object_or_404(Group,    id=grupo_id)
    elemento = get_object_or_404(Elemento, id=elemento_id)
 
    puede_ver  = request.POST.get('puede_ver',  'false').lower() == 'true'
    puede_usar = request.POST.get('puede_usar', 'false').lower() == 'true'
 
    # Si puede_usar=True, puede_ver debe ser True también (lógica)
    if puede_usar:
        puede_ver = True
 
    perm, _ = PermisoElemento.objects.update_or_create(
        group=grupo, elemento=elemento,
        defaults={'puede_ver': puede_ver, 'puede_usar': puede_usar}
    )
 
    return JsonResponse({
        'success':   True,
        'puede_ver': perm.puede_ver,
        'puede_usar': perm.puede_usar,
        'elemento':  elemento.label,
        'grupo':     grupo.name,
    })

########## VISTAS PARA LOGS ##########

# ══════════════════════════════════════════════════════════════
#  REGISTRO DE INTERACCIÓN CON ELEMENTOS (desde el frontend)
# ══════════════════════════════════════════════════════════════
@login_required
@require_POST
def registro_elemento(request):
    """
    Endpoint que recibe logs de interacción con elementos
    enviados desde el frontend via fetch.
    No interrumpe la acción del usuario — falla silenciosamente.
    """
    from .models import registrar_log, ActivityLog
 
    elemento_clave = request.POST.get('elemento_clave', '').strip()
    elemento_label = request.POST.get('elemento_label', '').strip()
    modulo_url     = request.POST.get('modulo_url', '').strip()
 
    if not elemento_clave:
        return JsonResponse({'success': False}, status=400)
 
    modulo = None
    if modulo_url:
        try:
            modulo = Modulo.objects.get(url_name=modulo_url, activo=True)
        except Modulo.DoesNotExist:
            pass
 
    registrar_log(
        request,
        tipo_evento    = 'elemento',
        descripcion    = f'Usó: {elemento_label or elemento_clave}',
        modulo         = modulo,
        elemento_clave = elemento_clave,
    )
    return JsonResponse({'success': True})

# ── Vista: logs del usuario en su perfil (ya autenticado) ────
@login_required
def perfil(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name  = request.POST.get('last_name', '')
        request.user.email      = request.POST.get('email', '')
        request.user.save()
        p = request.user.profile
        p.cargo    = request.POST.get('cargo', '')
        p.area     = request.POST.get('area', '')
        p.telefono = request.POST.get('telefono', '')
        if 'avatar' in request.FILES:
            p.avatar = request.FILES['avatar']
        p.save()
        return redirect('perfil')
 
    from .models import ActivityLog
    logs = ActivityLog.objects.filter(
        usuario=request.user
    ).select_related('modulo').order_by('-fecha')[:50]
 
    return render(request, "usuarios/perfil.html", {'logs': logs})
 
 
# ── Vista: logs de un usuario para el superadmin ─────────────
@superuser_required
def logs_usuario(request, id):
    from .models import ActivityLog
    usuario_visto = get_object_or_404(User, id=id)
 
    logs = ActivityLog.objects.filter(
        usuario=usuario_visto
    ).select_related('modulo').order_by('-fecha')
 
    return render(request, 'usuarios/logs_usuario.html', {
        'usuario_visto':   usuario_visto,
        'logs':            logs,
        'total_logs':      logs.count(),
        'total_login':     logs.filter(tipo_evento='login').count(),
        'total_modulos':   logs.filter(tipo_evento='modulo').count(),
        'total_elementos': logs.filter(tipo_evento='elemento').count(),
    })
 
 
# ── Vista: limpiar logs de un usuario (superadmin) ───────────
@superuser_required
@require_POST
def logs_limpiar_usuario(request, id):
    from .models import ActivityLog
    usuario_visto = get_object_or_404(User, id=id)
    eliminados = ActivityLog.objects.filter(usuario=usuario_visto).count()
    ActivityLog.objects.filter(usuario=usuario_visto).delete()
    return redirect('logs_usuario', id=id)


def error_403(request, exception=None):
    """
    Página 403 personalizada.
    Registra el intento de acceso denegado si el usuario está autenticado.
    """
    if request.user.is_authenticated:
        from .models import registrar_log
        url_name = ''
        modulo   = None
 
        if request.resolver_match:
            url_name = request.resolver_match.url_name or ''
 
        # Intentar vincular con un módulo registrado
        try:
            modulo = Modulo.objects.get(url_name=url_name, activo=True)
        except (Modulo.DoesNotExist, Exception):
            modulo = None
 
        registrar_log(
            request,
            tipo_evento    = 'acceso_denegado',
            descripcion    = f'Acceso denegado a: {url_name or request.path}',
            modulo         = modulo,
            elemento_clave = 'acceso_403',
        )
 
    return render(request, 'errors/403.html', status=403)
