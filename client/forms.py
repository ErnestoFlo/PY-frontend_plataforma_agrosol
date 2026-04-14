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