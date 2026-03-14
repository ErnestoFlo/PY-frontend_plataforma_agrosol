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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
