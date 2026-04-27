class ActivityLogMiddleware:
    """
    Registra automáticamente el acceso a módulos.
    Solo actúa en requests GET autenticados cuya URL
    coincida con el url_name de algún Modulo registrado.
    """

    URLS_EXCLUIDAS = {
        'login', 'logout', 'password_reset',
        'panel_permisos', 'lista_usuarios',
        'modulo_escanear', 'modulo_elementos',
        'guardar_permiso_elemento', 'grupo_gestionar_modulo',
        'grupo_crear', 'grupo_eliminar', 'grupo_asignar_usuario',
        'modulo_crear', 'modulo_eliminar', 'modulo_editar',
        'crear_usuario', 'editar_usuario', 'desactivar_usuario',
        'perfil', 'registro_elemento',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Solo loguear GET exitosos de usuarios autenticados no superusuarios
        if (
            request.method == 'GET'
            and response.status_code == 200
            and request.user.is_authenticated
            and not request.user.is_superuser
            and request.resolver_match
        ):
            url_name = request.resolver_match.url_name or ''

            if url_name and url_name not in self.URLS_EXCLUIDAS:
                self._intentar_log_modulo(request, url_name)

        return response

    def _intentar_log_modulo(self, request, url_name):
        """Busca el módulo por url_name y registra el acceso."""
        try:
            from .models import Modulo, registrar_log
            modulo = Modulo.objects.get(url_name=url_name, activo=True)
            registrar_log(
                request,
                tipo_evento = 'modulo',
                descripcion = f'Accedió a {modulo.nombre}',
                modulo      = modulo,
            )
        except Exception:
            pass