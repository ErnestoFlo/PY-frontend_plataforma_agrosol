from django import forms

class form_proveedores(forms.Form):
  proveedor = forms.CharField(label='', max_length=240)
  direccion = forms.CharField(label='', max_length=720)
  contacto = forms.CharField(label='', max_length=320)
  cargo = forms.CharField(label='', max_length=240)
  telefono = forms.CharField(label='', max_length=240)
  celular = forms.CharField(label='', max_length=240)
  email = forms.CharField(label='', max_length=400)
  terminos_de_pago = forms.CharField(label='', max_length=400)