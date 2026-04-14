from django.urls import path
from . import views

urlpatterns = [
    ### URLS DE PROVEEDORES
    path("proveedores/", views.list_proveedores, name="proveedores"),
    path("proveedores/crear/", views.create_or_edit_proveedor, name="proveedores_crear"),
    path("proveedores/editar/<int:id>/", views.create_or_edit_proveedor, name="proveedores_editar"),
    path("proveedores/confirmar/<int:id>/", views.confirm_delete, name="confirm_delete"),
    path("proveedores/eliminar/<int:id>/", views.delete_proveedor, name="proveedores_eliminar"),
    
    ### URLS DE DISEÑO
    path("design/test_components/", views.tests_components, name="tests_page"),
    path("design/test_form/", views.tests_form, name="test_form_page"),
    path("design/welcome/", views.welcome, name="welcome"),
    path("design/login/", views.login, name="login"),
    path("design/dashboard/", views.view1, name="dashboard"),
    
    ### URLS DE ENDPOINTS DINÁMICOS (HTMX)
    path("api/proveedores/opciones/", views.get_options, name="get_proveedores_options")
]