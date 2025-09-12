from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # Ruta para la página de inicio.
    path('', views.inicio, name="inicio"),
    # Ruta para mostrar la lista de productos.
    path('products/', views.porducts_views, name="products"),
    # Esta es la ruta que renderiza el formulario de creación de productos (GET).
    path('crear/', views.crear_producto_view_form, name="crear_producto"),
    # Esta ruta es el endpoint de la API para procesar la creación (POST).
    
    path('api/crear/', views.crear_producto, name="api_crear_producto"),
    
    path('products/<int:product_id>/editar/', views.editar_producto_form, name="editar_producto_form"),
    # Ruta para el endpoint de la API que procesa la edición (PUT)
    path('api/products/<int:product_id>/editar/', views.editar_producto, name="api_editar_producto"),
    # Ruta para eliminar un producto (POST)
    path('products/<int:product_id>/eliminar/', views.eliminar_producto, name="eliminar_producto"),
]