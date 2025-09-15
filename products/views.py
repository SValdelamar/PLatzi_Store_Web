from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
import json

# Página de inicio
def inicio(request):
    return render(request, "inicio.html")

# Listar productos
def porducts_views(request):
    """
    Obtiene la lista de productos desde la API y los pasa a la plantilla.
    """
    try:
        response = requests.get("https://api.escuelajs.co/api/v1/products", timeout=10)

        if response.status_code == 200:
            productos = response.json()
            return render(request, "lista_productos.html", {
                'productos': productos,
                'user_authenticated': request.user.is_authenticated
            })
        else:
            return render(request, "lista_productos.html", {'error': f"Error en la API: {response.status_code}"})

    except requests.exceptions.Timeout:
        return render(request, "lista_productos.html", {'error': 'Tiempo de espera agotado al conectar con la API.'})
    except requests.exceptions.ConnectionError:
        return render(request, "lista_productos.html", {'error': 'Error de conexión. Verifique su conexión a internet.'})
    except Exception as e:
        return render(request, "lista_productos.html", {'error': f'Ocurrió un error inesperado: {str(e)}'})


# ---------------------------
# CREAR PRODUCTO
# ---------------------------
@login_required
def crear_producto_view_form(request):
    """
    Obtiene la lista de categorías desde la API y renderiza
    el formulario para crear un nuevo producto.
    """
    try:
        response = requests.get("https://api.escuelajs.co/api/v1/categories", timeout=10)
        response.raise_for_status()
        categorias = response.json()

        categorias_limpias = [
            {'id': cat['id'], 'name': cat['name']}
            for cat in categorias
        ]

        return render(request, "crear_producto.html", {'categorias': categorias_limpias})

    except requests.exceptions.RequestException as e:
        messages.error(request, f"No se pudieron cargar las categorías. Error: {e}")
        return render(request, "crear_producto.html", {'categorias': []})


@login_required
@require_http_methods(["POST"])
def crear_producto(request):
    """
    Procesa la creación de un nuevo producto usando la API externa.
    """
    try:
        data = json.loads(request.body)
        nombre = data.get("nombre")
        precio = data.get("precio")
        descripcion = data.get("descripcion")
        categoria_id = data.get("categoriaId")
        imagen_url = data.get("imagen")

        if not all([nombre, precio, descripcion, categoria_id, imagen_url]):
            return JsonResponse({'success': False, 'error': 'Todos los campos son requeridos'}, status=400)

        productos_data = {
            "title": nombre,
            "price": float(precio),
            "description": descripcion,
            "categoryId": int(categoria_id),
            "images": [imagen_url],
        }

        subir_respuesta = requests.post("https://api.escuelajs.co/api/v1/products/", json=productos_data, timeout=10)
        subir_respuesta.raise_for_status()

        if subir_respuesta.status_code == 201:
            datos = subir_respuesta.json()
            return JsonResponse({'success': True, 'data': datos})
        else:
            return JsonResponse({
                'success': False,
                'error': f'Error en la API: {subir_respuesta.status_code} - {subir_respuesta.text}'
            }, status=subir_respuesta.status_code)

    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Formato de datos no válido.'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'success': False, 'error': f'Error de conexión con la API: {str(e)}'}, status=500)


# ---------------------------
# EDITAR PRODUCTO
# ---------------------------
@login_required
def editar_producto_form(request, product_id):
    """
    Obtiene los datos de un producto específico para prellenar el formulario de edición.
    """
    try:
        response = requests.get(f"https://api.escuelajs.co/api/v1/products/{product_id}", timeout=10)
        response.raise_for_status()
        producto = response.json()
        return render(request, "editar_producto.html", {'producto': producto})
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al obtener el producto para editar: {e}")
        return redirect('products:products')


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def editar_producto(request, product_id):
    """
    Actualiza un producto existente usando la API externa (PUT).
    """
    try:
        data = json.loads(request.body)
        title = data.get("title")
        price = data.get("price")
        description = data.get("description")
        category_id = data.get("categoryId")
        images = data.get("images")

        if not all([title, price, description, category_id, images]):
            return JsonResponse({
                'success': False,
                'error': 'Título, precio, descripción, categoría e imágenes son requeridos.'
            }, status=400)

        productos_data = {
            "title": title,
            "price": float(price),
            "description": description,
            "categoryId": int(category_id),
            "images": images if isinstance(images, list) else [images],
        }

        subir_respuesta = requests.put(f"https://api.escuelajs.co/api/v1/products/{product_id}", json=productos_data, timeout=10)
        subir_respuesta.raise_for_status()

        if subir_respuesta.status_code == 200:
            return JsonResponse({'success': True, 'data': subir_respuesta.json()})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato de datos JSON no válido.'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'success': False, 'error': f'Error de conexión con la API: {str(e)}'}, status=500)


# ---------------------------
# ELIMINAR PRODUCTO
# ---------------------------
@login_required
@require_http_methods(["POST"])
def eliminar_producto(request, product_id):
    """
    Elimina un producto existente usando la API externa.
    """
    try:
        response = requests.delete(f"https://api.escuelajs.co/api/v1/products/{product_id}", timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            messages.success(request, "Producto eliminado exitosamente.")
        else:
            messages.error(request, "Hubo un problema al eliminar el producto.")

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error de conexión al intentar eliminar el producto: {e}")

    return redirect('products:products')


# ---------------------------
# PAGAR PRODUCTO (PUBLICO)
# ---------------------------
def pagar_producto(request, product_id):
    """
    Muestra el formulario de pago para un producto específico.
    """
    try:
        # Llamada a la API para obtener el producto
        response = requests.get(f"https://api.escuelajs.co/api/v1/products/{product_id}", timeout=10)
        response.raise_for_status()
        producto = response.json()

        # Enviamos el producto al template
        return render(request, "pagar_producto.html", {'producto': producto})

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al obtener el producto para pago: {e}")
        return redirect('products:products')
