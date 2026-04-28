# ══════════════════════════════════════════════════════════════
#  PASO 3 — SEÑALES DE LOGIN/LOGOUT
#  Crea el archivo: client/signals.py
# ══════════════════════════════════════════════════════════════
 
# ── client/signals.py ────────────────────────────────────────
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    """Registra automáticamente cada inicio de sesión."""
    from .models import registrar_log
    registrar_log(
        request,
        tipo_evento = 'login',
        descripcion = 'Inicio de sesión exitoso',
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Registra automáticamente cada cierre de sesión."""
    if user and user.is_authenticated:
        from .models import registrar_log
        registrar_log(
            request,
            tipo_evento = 'logout',
            descripcion = 'Cierre de sesión',
        )