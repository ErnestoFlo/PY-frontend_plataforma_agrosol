from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=60, default='bi-grid')
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
 
    def __str__(self):
        return self.nombre
    
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
def get_permisos(user, modulo_slug):
    """
    Retorna un dict con los permisos del usuario para un módulo.
 
    Ejemplo de resultado:
    {
        'seccion_info_personal': {'ver': True,  'usar': True},
        'campo_telefono':        {'ver': True,  'usar': False},
        'boton_eliminar':        {'ver': False, 'usar': False},
        'columna_email':         {'ver': True,  'usar': True},
    }
 
    Regla: el superusuario siempre tiene todos los permisos.
    Si el usuario pertenece a varios grupos, se aplica
    la unión (OR) de todos sus permisos.
    """
 
    # Superusuario → acceso total sin consultar la BD
    if user.is_superuser:
        try:
            modulo = Modulo.objects.get(slug=modulo_slug, activo=True)
            return {
                c.clave: {'ver': True, 'usar': True}
                for c in modulo.componentes.filter(activo=True)
            }
        except Modulo.DoesNotExist:
            return {}
 
    # Obtener todos los grupos del usuario
    grupos = user.groups.all()
    if not grupos.exists():
        return {}
 
    try:
        modulo = Modulo.objects.get(slug=modulo_slug, activo=True)
    except Modulo.DoesNotExist:
        return {}
 
    # Obtener todos los componentes del módulo
    componentes = modulo.componentes.filter(activo=True)
 
    # Construir el dict de permisos aplicando OR entre grupos
    resultado = {}
    for comp in componentes:
        permisos_comp = PermisoGrupo.objects.filter(
            group__in=grupos,
            componente=comp
        )
        puede_ver  = permisos_comp.filter(puede_ver=True).exists()
        puede_usar = permisos_comp.filter(puede_usar=True).exists()
        resultado[comp.clave] = {
            'ver':  puede_ver,
            'usar': puede_usar,
        }
 
    return resultado