from django import forms
from django import forms
from .services import PlatziAPIService

from django import forms

class CrearProductoForm(forms.Form):
    crear_producto = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
        label="Nombre del producto"
    )
    crear_precio = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Precio del producto'}),
        label="Precio del producto"
    )
    crear_descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del producto'}),
        label="Descripción del producto"
    )
    crear_categoria = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría del producto'}),
        label="Categoría del producto"
    )
    crear_imagen = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Imagen del producto'}),
        label="Imagen del producto"
    )

    def clean(self):
        cleaned_data = super().clean()
        # Aquí podrías añadir validaciones adicionales si las necesitas.
        # Por ejemplo, verificar si el nombre del producto ya existe en la base de datos.
        return cleaned_data