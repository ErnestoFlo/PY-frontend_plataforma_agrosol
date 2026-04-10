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
    path("proveedores/confirm-delete/<int:id>/", views.confirm_delete, name="confirm_delete"),
    path("proveedores/eliminar/<int:id>/", views.delete_proveedor, name="proveedores_eliminar"),
    ### URLS DE DISEÑO
    path("design/test_components/", views.tests_views, name="tests_page"),
    path("design/test_form/", views.tests_form, name="test_form_page"),
    path("design/welcome/", views.welcome, name="welcome"),
    path("design/login/", views.login, name="login"),
    path("design/dashboard/", views.view1, name="dashboard"),
    path("proveedores/obtener_opciones/", views.get_options, name="get_proveedores_options")
]