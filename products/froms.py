from django import forms
from django import forms
from .services import PlatziAPIService

class Crear_Producto_Form (forms.Form):
    crear_producto = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'})
        )
    crear_precio = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Precio del producto'})
        )
    crear_descripcion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del producto'})
        )
    crear_imagen = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Imagen del producto'})
        )
def clean_Crear_Producto_Form(self):
    crear_producto = self.cleaned_data.get('crear_producto')
    crear_precio = self.cleaned_data.get('crear_precio')
    crear_descripcion = self.cleaned_data.get('crear_descripcion')
    crear_imagen = self.cleaned_data.get('crear_imagen')
    if not crear_producto or not crear_precio or not crear_descripcion or not crear_imagen:
        raise forms.ValidationError('Todos los campos son requeridos')
    return self.cleaned_data 
