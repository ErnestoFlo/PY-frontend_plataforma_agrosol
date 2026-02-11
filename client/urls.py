from django.urls import path
from . import views

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
    path("proveedores/eliminar/<int:id>", views.delete_proveedor, name="proveedores_eliminar")
]