from django import forms

class ProveedoresForm(forms.Form):
  proveedor = forms.CharField(max_length=240)
  direccion = forms.CharField(max_length=720)
  contacto = forms.CharField(max_length=320)
  cargo = forms.CharField(max_length=240)
  telefono = forms.CharField(max_length=240)
  celular = forms.CharField(max_length=240)
  email = forms.CharField(max_length=400)
  terminos_de_pago = forms.CharField(max_length=400)

# Formularios de Login y Búsqueda de prueba, usado solamente por testeo
class LoginForm(forms.Form):
  usuario = forms.CharField(max_length=240)
  contrasenia = forms.CharField(max_length=720)

class SearchForm(forms.Form):
  query = forms.CharField(max_length=240, required=False)