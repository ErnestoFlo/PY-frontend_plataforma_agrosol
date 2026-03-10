from django.db import models
from django.contrib.auth.models import User
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