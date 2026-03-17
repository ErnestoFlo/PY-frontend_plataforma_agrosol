from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    ### URLS DE EJEMPLO ###
    path("", views.listar, name="listar"),
    path("nuevo/", views.crear, name="crear"),
    path("editar/<int:id>", views.editar, name="editar"),
    path("eliminar/<int:id>", views.eliminar, name="eliminar"),
    ### URLS DE PROVEEDORES
    path("proveedores/", views.list_proveedores, name="proveedores"),
    path("proveedores/crear", views.create_proveedor, name="proveedores_crear"),
    path("proveedores/editar/<int:id>", views.edit_proveedor, name="proveedores_editar"),
    path("proveedores/eliminar/<int:id>", views.delete_proveedor, name="proveedores_eliminar"),

    ### URLS DE LOGIN ###
    path("principio/", views.principio, name="principio"),

    ### URLS DE USUARIOS ###
    path("usuarios/", views.lista_usuarios, name="lista_usuarios"),
    path("usuarios/editar/<int:id>/", views.editar_usuario, name="editar_usuario"),
    path("usuarios/desactivar/<int:id>/", views.desactivar_usuario, name="desactivar_usuario"),
    path("perfil/", views.perfil, name="perfil"),
    path("test-400/", views.test_400, name="test_400"),

    ### URLS DE PERMISOS ###
    path("permisos/", views.panel_permisos, name="panel_permisos"),
    path("permisos/grupos/crear/", views.grupo_crear, name="grupo_crear"),
    path("permisos/grupos/<int:id>/eliminar/", views.grupo_eliminar, name="grupo_eliminar"),
    path("permisos/grupos/<int:id>/", views.grupo_editar_permisos, name="grupo_editar_permisos"),
    path("permisos/grupos/<int:id>/guardar/", views.grupo_guardar_permisos, name="grupo_guardar_permisos"),
    path("permisos/grupos/<int:id>/usuarios/", views.grupo_asignar_usuario, name="grupo_asignar_usuario"),
    path("prueba-tecnica/", views.prueba_tecnica, name="prueba_tecnica"),
    # Módulos
    # path("permisos/modulos/crear/", views.modulo_crear, name="modulo_crear"),
    # path("permisos/modulos/<int:id>/eliminar/", views.modulo_eliminar, name="modulo_eliminar"),
    # path("permisos/modulos/<int:modulo_id>/elementos/crear/", views.elemento_crear, name="elemento_crear"),
    # path("permisos/elementos/<int:id>/eliminar/", views.elemento_eliminar, name="elemento_eliminar"),
    # # Grupos — acceso a módulo (nivel 1)
    # path("permisos/grupos/<int:id>/acceso/", views.grupo_guardar_acceso_modulo, name="grupo_guardar_acceso"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
