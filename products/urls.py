from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path('', views.inicio, name="inicio"),
    path('products/', views.porducts_views, name="products"),

    # Crear producto
    path('crear/', views.crear_producto_view_form, name="crear_producto"),
    path('api/crear/', views.crear_producto, name="api_crear_producto"),

    # Editar producto
    path('products/editar/<int:product_id>', views.editar_producto_form, name="editar_producto_form"),
    path('api/products/<int:product_id>/editar/', views.editar_producto, name="api_editar_producto"),

    # Eliminar producto
    path('products/<int:product_id>/eliminar/', views.eliminar_producto, name="eliminar_producto"),
    path('pagar/<int:product_id>/', views.pagar_producto, name='pagar'),  # <--- NUEVA RUTA

]
