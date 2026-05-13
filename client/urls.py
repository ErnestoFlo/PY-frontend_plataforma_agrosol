from django.urls import path
from . import views
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static


urlpatterns = [
    ### BIENVENIDA
    path("landing_login/", views.landing_login, name="landing"),
    path("dashboard/", views.view1, name="dashboard"),
    ### URLS DE PROVEEDORES
    path("proveedores/", views.list_proveedores, name="proveedores"),
    path("proveedores/crear/", views.create_or_edit_proveedor, name="proveedores_crear"),
    path("proveedores/editar/<int:id>/", views.create_or_edit_proveedor, name="proveedores_editar"),
    path("proveedores/confirmar/<int:id>/", views.confirm_delete, name="confirm_delete"),
    path("proveedores/eliminar/<int:id>/", views.delete_proveedor, name="proveedores_eliminar"),

    ### URLS DE DISEÑO
    path("design/test_components/", views.tests_components, name="tests_page"),
    
    ### URLS DE ENDPOINTS DINÁMICOS (HTMX)
    path("api/opciones/", views.get_options, name="get_proveedores_options"),

    ### URLS DE USUARIOS ###
    path("usuarios/", views.lista_usuarios, name="lista_usuarios"),
    path("usuarios/editar/<int:id>/", views.editar_usuario, name="editar_usuario"),
    path("usuarios/desactivar/<int:id>/", views.desactivar_usuario, name="desactivar_usuario"),
    path("perfil/", views.perfil, name="perfil"),
    path("test-400/", views.test_400, name="test_400"),
    path("usuarios/crear/", views.crear_usuario, name="crear_usuario"),

    ### URLS DE PERMISOS ###
    path("permisos/", views.panel_permisos, name="panel_permisos"),
    path("permisos/grupos/crear/", views.grupo_crear, name="grupo_crear"),
    path("permisos/grupos/<int:id>/eliminar/", views.grupo_eliminar, name="grupo_eliminar"),
    path("permisos/grupos/<int:id>/", views.grupo_editar_permisos, name="grupo_editar_permisos"),
    path("permisos/grupos/<int:id>/guardar/", views.grupo_guardar_permisos, name="grupo_guardar_permisos"),
    path("permisos/grupos/<int:id>/usuarios/", views.grupo_asignar_usuario, name="grupo_asignar_usuario"),
    path("permisos/modulos/crear/",             views.modulo_crear,           name="modulo_crear"),
    path("permisos/modulos/<int:id>/eliminar/",  views.modulo_eliminar,        name="modulo_eliminar"),
    path("permisos/grupos/<int:id>/modulos/",    views.grupo_gestionar_modulo, name="grupo_gestionar_modulo"),
    path("permisos/modulos/<int:id>/editar/", views.modulo_editar, name="modulo_editar"),
    path("permisos/modulos/<int:id>/escanear/", views.modulo_escanear, name="modulo_escanear"),
    path("permisos/modulos/<int:id>/elementos/", views.modulo_elementos, name="modulo_elementos"), # Obtener elementos de un módulo (con permisos de un grupo)
    path("permisos/grupos/<int:grupo_id>/elementos/<int:elemento_id>/guardar/", views.grupo_guardar_permisos_elemento, name="guardar_permiso_elemento"), # Guardar permiso ver/usar de un elemento para un grupo 

    ### PRUEBAS TECNICAS ###
    path("prueba-tecnica/", views.prueba_tecnica, name="prueba_tecnica"),

    ### LOGS ###
    path("logs/elemento/", views.registro_elemento, name="registro_elemento"),
    path("usuarios/<int:id>/logs/",         views.logs_usuario,        name="logs_usuario"),
    path("usuarios/<int:id>/logs/limpiar/", views.logs_limpiar_usuario, name="logs_limpiar_usuario")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)