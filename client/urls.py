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

    ### Pruebas de login ###
    path("principio/", views.principio, name="principio"),
    path("perfil/", views.perfil, name="perfil")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
