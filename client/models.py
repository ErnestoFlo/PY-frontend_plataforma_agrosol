from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify as _slugify
import os
from django.conf import settings
from bs4 import BeautifulSoup
from django.template.loader import get_template
from django.template import TemplateDoesNotExist


class UserProfile(models.Model):
    # Relación uno a uno con el User de Django
    user     = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Campos extra que quieras agregar
    avatar   = models.ImageField(upload_to='avatars/', blank=True, null=True)
    cargo    = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20,  blank=True)
    area     = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
# Cada vez que se crea un User, crear su perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.profile.save()

# ════════════════════════════════════════════════════════════════
#  MÓDULO — Representa una pantalla o sección del sistema
# ════════════════════════════════════════════════════════════════
class Modulo(models.Model):
    """Representa una pantalla/sección del sistema."""
    nombre    = models.CharField(max_length=100, unique=True)
    slug      = models.SlugField(max_length=100, unique=True)
    icono     = models.CharField(max_length=60, default='bi-grid',
                                 help_text='Clase de Bootstrap Icons. Ej: bi-people')
    url_name  = models.CharField(max_length=100, blank=True,
                                 help_text='Nombre de la URL en urls.py. Ej: lista_usuarios')
    descripcion = models.CharField(max_length=255, blank=True)
    orden     = models.PositiveIntegerField(default=0)
    activo    = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ['orden', 'nombre']
        verbose_name        = 'Módulo'
        verbose_name_plural = 'Módulos'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slugify(self.nombre)
        super().save(*args, **kwargs)
    
# ════════════════════════════════════════════════════════════════
#  COMPONENTE — Elemento específico dentro de un módulo
#  Puede ser: campo, botón, columna de tabla, sección, etc.
# ════════════════════════════════════════════════════════════════
TIPO_COMPONENTE = [
    ('seccion', 'Sección completa'),
    ('campo',   'Campo del formulario'),
    ('boton',   'Botón de acción'),
    ('columna', 'Columna de tabla'),
]
 
class Componente(models.Model):
    modulo      = models.ForeignKey(
                    Modulo,
                    on_delete=models.CASCADE,
                    related_name='componentes'
                  )
    nombre      = models.CharField(max_length=100)
    # clave única usada en el template: permisos.boton_eliminar
    clave       = models.SlugField(max_length=100)
    tipo        = models.CharField(max_length=20, choices=TIPO_COMPONENTE)
    descripcion = models.CharField(max_length=255, blank=True)
    orden       = models.PositiveIntegerField(default=0)
    activo      = models.BooleanField(default=True)
 
    class Meta:
        ordering            = ['orden', 'nombre']
        unique_together     = ('modulo', 'clave')
        verbose_name        = 'Componente'
        verbose_name_plural = 'Componentes'
 
    def __str__(self):
        return f"{self.modulo.nombre} → {self.nombre}"
    
# ════════════════════════════════════════════════════════════════
#  PERMISO DE GRUPO — Qué puede hacer cada grupo en cada componente
#  ver:  el componente es visible
#  usar: el componente es interactuable (editar, click, etc.)
# ════════════════════════════════════════════════════════════════
class PermisoGrupo(models.Model):
    group      = models.ForeignKey(
                    Group,
                    on_delete=models.CASCADE,
                    related_name='permisos_granulares'
                 )
    componente = models.ForeignKey(
                    Componente,
                    on_delete=models.CASCADE,
                    related_name='permisos'
                 )
    puede_ver  = models.BooleanField(default=False)
    puede_usar = models.BooleanField(default=False)
 
    class Meta:
        unique_together     = ('group', 'componente')
        verbose_name        = 'Permiso de Grupo'
        verbose_name_plural = 'Permisos de Grupos'
 
    def __str__(self):
        ver = '👁' if self.puede_ver  else '✗'
        uso = '✎' if self.puede_usar else '✗'
        return f"{self.group.name} | {self.componente} | ver:{ver} usar:{uso}"

# ════════════════════════════════════════════════════════════════
#  FUNCIÓN HELPER — Obtener permisos de un usuario para un módulo
#  Uso en las vistas:
#      permisos = get_permisos(request.user, 'usuarios')
#  Uso en los templates:
#      {% if permisos.boton_eliminar.ver %}
# ════════════════════════════════════════════════════════════════
# def get_permisos(user, modulo_slug):
#     """
#     Retorna un dict con los permisos del usuario para un módulo.
 
#     Ejemplo de resultado:
#     {
#         'seccion_info_personal': {'ver': True,  'usar': True},
#         'campo_telefono':        {'ver': True,  'usar': False},
#         'boton_eliminar':        {'ver': False, 'usar': False},
#         'columna_email':         {'ver': True,  'usar': True},
#     }
 
#     Regla: el superusuario siempre tiene todos los permisos.
#     Si el usuario pertenece a varios grupos, se aplica
#     la unión (OR) de todos sus permisos.
#     """
 
#     # Superusuario → acceso total sin consultar la BD
#     if user.is_superuser:
#         try:
#             modulo = Modulo.objects.get(slug=modulo_slug, activo=True)
#             return {
#                 c.clave: {'ver': True, 'usar': True}
#                 for c in modulo.componentes.filter(activo=True)
#             }
#         except Modulo.DoesNotExist:
#             return {}
 
#     # Obtener todos los grupos del usuario
#     grupos = user.groups.all()
#     if not grupos.exists():
#         return {}
 
#     try:
#         modulo = Modulo.objects.get(slug=modulo_slug, activo=True)
#     except Modulo.DoesNotExist:
#         return {}
 
#     # Obtener todos los componentes del módulo
#     componentes = modulo.componentes.filter(activo=True)
 
#     # Construir el dict de permisos aplicando OR entre grupos
#     resultado = {}
#     for comp in componentes:
#         permisos_comp = PermisoGrupo.objects.filter(
#             group__in=grupos,
#             componente=comp
#         )
#         puede_ver  = permisos_comp.filter(puede_ver=True).exists()
#         puede_usar = permisos_comp.filter(puede_usar=True).exists()
#         resultado[comp.clave] = {
#             'ver':  puede_ver,
#             'usar': puede_usar,
#         }
 
#     return resultado


class AccesoModulo(models.Model):
    """
    Nivel 1 de permisos — ¿puede el grupo entrar al módulo?
    Si tiene_acceso = False, el usuario ve 403 al intentar entrar.
    """
    group        = models.ForeignKey(
                     'auth.Group',
                     on_delete=models.CASCADE,
                     related_name='accesos_modulos'
                   )
    modulo       = models.ForeignKey(
                     Modulo,
                     on_delete=models.CASCADE,
                     related_name='accesos'
                   )
    tiene_acceso = models.BooleanField(default=True)

    class Meta:
        unique_together     = ('group', 'modulo')
        verbose_name        = 'Acceso a Módulo'
        verbose_name_plural = 'Accesos a Módulos'

    def __str__(self):
        icono = '✅' if self.tiene_acceso else '🚫'
        return f"{icono} {self.group.name} → {self.modulo.nombre}"


# ══════════════════════════════════════════════════════════════
#  HELPER — usar en cualquier vista protegida
# ══════════════════════════════════════════════════════════════

def tiene_acceso_modulo(user, url_name):
    if user.is_superuser:
        return True
 
    grupos = user.groups.all()
    if not grupos.exists():
        return False
 
    try:
        modulo = Modulo.objects.get(url_name=url_name, activo=True)
    except Modulo.DoesNotExist:
        # Si no hay módulo registrado con ese url_name
        # la vista NO está protegida → se permite el acceso
        return True
 
    return AccesoModulo.objects.filter(
        group__in=grupos,
        modulo=modulo,
        tiene_acceso=True
    ).exists()
 
 
# ── Modelo Elemento ──────────────────────────────────────────
# (Agrégalo después de AccesoModulo)
 
TIPO_ELEMENTO = [
    ('accion',     'Acción'),
    ('componente', 'Componente'),
    ('dato',       'Dato'),
]
 
class Elemento(models.Model):
    # Representa un elemento interactivo dentro de un módulo.
    # Se detecta automáticamente desde el HTML via data-permiso.
    modulo      = models.ForeignKey(
                    Modulo,
                    on_delete=models.CASCADE,
                    related_name='elementos'
                  )
    clave       = models.CharField(max_length=100)   # valor de data-permiso
    tipo        = models.CharField(max_length=20, choices=TIPO_ELEMENTO)
    label       = models.CharField(max_length=150)   # valor de data-label
    orden       = models.PositiveIntegerField(default=0)
    activo      = models.BooleanField(default=True)
 
    class Meta:
        ordering        = ['tipo', 'orden', 'clave']
        unique_together = ('modulo', 'clave')
        verbose_name        = 'Elemento'
        verbose_name_plural = 'Elementos'
 
    def __str__(self):
        return f"{self.modulo.nombre} → [{self.tipo}] {self.label}"
 
 
# ── Modelo PermisoElemento ───────────────────────────────────
 
class PermisoElemento(models.Model):
    # Nivel 2 de permisos — ¿qué puede hacer el grupo con cada elemento?
    # puede_ver  = el elemento existe en el DOM (se renderiza)
    # puede_usar = el elemento está habilitado (no disabled)
    group      = models.ForeignKey(
                   'auth.Group',
                   on_delete=models.CASCADE,
                   related_name='permisos_elementos'
                 )
    elemento   = models.ForeignKey(
                   Elemento,
                   on_delete=models.CASCADE,
                   related_name='permisos'
                 )
    puede_ver  = models.BooleanField(default=True)
    puede_usar = models.BooleanField(default=True)
 
    class Meta:
        unique_together     = ('group', 'elemento')
        verbose_name        = 'Permiso de Elemento'
        verbose_name_plural = 'Permisos de Elementos'
 
    def __str__(self):
        return f"{self.group.name} | {self.elemento.label} | ver:{self.puede_ver} usar:{self.puede_usar}"
 
 
# ── Función escanear_template ────────────────────────────────
 
def _get_carpetas_templates():
    """
    Escanea automáticamente todas las subcarpetas de templates
    disponibles en el proyecto (DIRS + APP_DIRS).
 
    Retorna una lista de rutas relativas como:
        ['', 'client', 'permisos', 'proveedores', 'client/permisos', ...]
    """
    carpetas = set()
    carpetas.add('')  # raíz siempre incluida
 
    # 1. Carpetas declaradas en settings.TEMPLATES[x]['DIRS']
    for tmpl_conf in settings.TEMPLATES:
        for tmpl_dir in tmpl_conf.get('DIRS', []):
            if os.path.exists(tmpl_dir):
                for root, dirs, files in os.walk(tmpl_dir):
                    # Ignorar carpetas ocultas y __pycache__
                    dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
                    rel = os.path.relpath(root, tmpl_dir).replace('\\', '/')
                    if rel != '.':
                        carpetas.add(rel)
 
    # 2. Carpetas de cada app instalada (cuando APP_DIRS=True)
    from django.apps import apps as django_apps
    for app_config in django_apps.get_app_configs():
        tmpl_path = os.path.join(app_config.path, 'templates')
        if os.path.exists(tmpl_path):
            for root, dirs, files in os.walk(tmpl_path):
                dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
                rel = os.path.relpath(root, tmpl_path).replace('\\', '/')
                if rel == '.':
                    carpetas.add('')
                else:
                    carpetas.add(rel)
 
    return sorted(carpetas, key=lambda x: (len(x), x))
 
 
def escanear_template(modulo):
    """
    Escanea el template del módulo buscando elementos con data-permiso.
    Registra automáticamente los Elemento encontrados en la BD.
 
    No requiere configuración manual de rutas — detecta todas las
    carpetas de templates del proyecto automáticamente.
 
    Retorna:
    {
        'creados':    [{'clave': ..., 'tipo': ..., 'label': ...}],
        'existentes': [...],
        'total':      27,
        'ruta':       'ruta/absoluta/al/template.html',
    }
    o en caso de error:
    {
        'error': 'Mensaje descriptivo del problema',
    }
    """
    if not modulo.url_name:
        return {'error': 'El módulo no tiene url_name configurado.'}
 
    url_name = modulo.url_name
 
    # ── Construir lista de nombres a buscar ──────────────────
    # Usando todas las carpetas detectadas automáticamente
    carpetas       = _get_carpetas_templates()
    posibles_nombres = []
 
    for carpeta in carpetas:
        if carpeta:
            posibles_nombres.append(f'{carpeta}/{url_name}.html')
        else:
            posibles_nombres.append(f'{url_name}.html')
 
    # ── Buscar el template usando el sistema de Django ───────
    html           = None
    template_usado = None
 
    for nombre in posibles_nombres:
        try:
            tmpl           = get_template(nombre)
            template_usado = tmpl.origin.name  # ruta física absoluta
            with open(template_usado, 'r', encoding='utf-8') as f:
                html = f.read()
            break  # encontrado — salir del loop
        except TemplateDoesNotExist:
            continue
        except (OSError, AttributeError):
            continue
 
    if not html:
        return {
            'error': (
                f'No se encontró el template para "{url_name}". '
                f'Carpetas buscadas automáticamente: '
                f'{[n for n in posibles_nombres[:8]]}... '
                f'({len(posibles_nombres)} rutas en total). '
                f'Verifica que el url_name coincida exactamente '
                f'con el nombre del archivo .html.'
            )
        }
 
    # ── Parsear el HTML y extraer elementos data-permiso ─────
    soup              = BeautifulSoup(html, 'html.parser')
    elementos_en_html = soup.find_all(attrs={'data-permiso': True})
 
    if not elementos_en_html:
        return {
            'error': (
                f'Template encontrado en "{template_usado}" pero no '
                f'contiene elementos con data-permiso. '
                f'Asegúrate de haber marcado los elementos con '
                f'data-permiso, data-tipo y data-label.'
            ),
            'ruta': template_usado,
        }
 
    # ── Registrar elementos en la BD ─────────────────────────
    ORDEN_TIPO = {'accion': 1, 'componente': 2, 'dato': 3}
 
    creados    = []
    existentes = []
 
    for i, tag in enumerate(elementos_en_html):
        clave = tag.get('data-permiso', '').strip()
        tipo  = tag.get('data-tipo',    'componente').strip()
        label = tag.get('data-label',   clave).strip()
 
        if not clave:
            continue
 
        # Validar tipo
        if tipo not in ['accion', 'componente', 'dato']:
            tipo = 'componente'
 
        orden = ORDEN_TIPO.get(tipo, 2) * 100 + i
 
        obj, fue_creado = Elemento.objects.get_or_create(
            modulo=modulo,
            clave=clave,
            defaults={
                'tipo':  tipo,
                'label': label,
                'orden': orden,
            }
        )
 
        # Si el label cambió en el HTML, lo actualizamos en BD
        if not fue_creado and obj.label != label:
            obj.label = label
            obj.save(update_fields=['label'])
 
        if fue_creado:
            creados.append({'clave': clave, 'tipo': tipo, 'label': label})
        else:
            existentes.append({'clave': clave, 'tipo': tipo, 'label': label})
 
    return {
        'creados':    creados,
        'existentes': existentes,
        'total':      len(creados) + len(existentes),
        'ruta':       template_usado,
    }

 
# ── Función get_permisos actualizada ────────────────────────
 
def get_permisos(user, url_name):
    # Nivel 2 — ¿Qué puede ver/usar el usuario dentro del módulo?
 
    # Retorna dict indexado por clave:
    # {
    #     'btn_crear':   {'ver': True,  'usar': True,  'tipo': 'accion'},
    #     'btn_eliminar':{'ver': True,  'usar': False, 'tipo': 'accion'},
    #     'c_textbox':   {'ver': True,  'usar': True,  'tipo': 'componente'},
    #     'tabla_datos': {'ver': False, 'usar': False, 'tipo': 'dato'},
    # }
 
    # Si el usuario es superusuario → todo True.
    # Si no hay PermisoElemento para un grupo → usa el default (ver=True, usar=True).

    try:
        modulo = Modulo.objects.get(url_name=url_name, activo=True)
    except Modulo.DoesNotExist:
        return {}
 
    elementos = modulo.elementos.filter(activo=True)
    if not elementos.exists():
        return {}
 
    # Superusuario → acceso total
    if user.is_superuser:
        return {
            e.clave: {'ver': True, 'usar': True, 'tipo': e.tipo}
            for e in elementos
        }
 
    grupos = user.groups.all()
 
    resultado = {}
    for elem in elementos:
        perms = PermisoElemento.objects.filter(group__in=grupos, elemento=elem)
        if perms.exists():
            resultado[elem.clave] = {
                'ver':  perms.filter(puede_ver=True).exists(),
                'usar': perms.filter(puede_usar=True).exists(),
                'tipo': elem.tipo,
            }
        else:
            # Sin configuración explícita → acceso completo por defecto
            resultado[elem.clave] = {
                'ver': True, 'usar': True, 'tipo': elem.tipo
            }
 
    return resultado