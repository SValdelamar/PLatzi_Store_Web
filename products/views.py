from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import requests
import json


def inicio(request):
    """
    Renderiza la página de inicio.
    """
    return render(request, "inicio.html")


def porducts_views(request):
    """
    Obtiene la lista de productos desde la API y los pasa a la plantilla.
    """
    try:
        response = requests.get("https://api.escuelajs.co/api/v1/products", timeout=10)

        if response.status_code == 200:
            productos = response.json()
            return render(request, "lista_productos.html", {'productos': productos})
        else:
            return render(request, "lista_productos.html", {'error': f"Error en la API: {response.status_code}"})

    except requests.exceptions.Timeout:
        return render(request, "lista_productos.html", {'error': 'Tiempo de espera agotado al conectar con la API.'})
    except requests.exceptions.ConnectionError:
        return render(request, "lista_productos.html", {'error': 'Error de conexión. Verifique su conexión a internet.'})
    except Exception as e:
        return render(request, "lista_productos.html", {'error': f'Ocurrió un error inesperado: {str(e)}'})


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
    except Exception as e:
        messages.error(request, f"Ocurrió un error inesperado: {str(e)}")
        return render(request, "crear_producto.html", {'categorias': []})


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

        base_url = "https://api.escuelajs.co/api/v1/"
        subir_respuesta = requests.post(f"{base_url}products/", json=productos_data, timeout=10)
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
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)


def editar_producto_form(request, product_id):
    """
    Obtiene los datos de un producto específico para prellenar el formulario de edición.
    """
    try:
        response = requests.get(f"https://api.escuelajs.co/api/v1/products/{product_id}")
        response.raise_for_status()
        producto = response.json()
        return render(request, "editar_producto.html", {'producto': producto})
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al obtener el producto para editar: {e}")
        return redirect('products:products')
    except Exception as e:
        messages.error(request, f"Ocurrió un error inesperado: {e}")
        return redirect('products:products')


@csrf_exempt
@require_http_methods(["PUT"])
def editar_producto(request, product_id):
    """
    Actualiza un producto existente usando la API externa (PUT).
    """
    try:
        data = json.loads(request.body)

        # Recuperar datos enviados desde el frontend
        title = data.get("title")
        price = data.get("price")
        description = data.get("description")
        category_id = data.get("categoryId")
        images = data.get("images")

        # Validar que todos los campos estén presentes
        if not all([title, price, description, category_id, images]):
            return JsonResponse({
                'success': False,
                'error': 'Título, precio, descripción, categoría e imágenes son requeridos.'
            }, status=400)

        # Preparar datos para la API
        productos_data = {
            "title": title,
            "price": float(price),
            "description": description,
            "categoryId": int(category_id),
            "images": images if isinstance(images, list) else [images],
        }

        base_url = "https://api.escuelajs.co/api/v1/"
        subir_respuesta = requests.put(f"{base_url}products/{product_id}", json=productos_data, timeout=10)
        subir_respuesta.raise_for_status()

        if subir_respuesta.status_code == 200:
            return JsonResponse({'success': True, 'data': subir_respuesta.json()})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato de datos JSON no válido.'}, status=400)

    except requests.exceptions.HTTPError as e:
        return JsonResponse({
            'success': False,
            'error': f'Error en la API: {e.response.status_code} - {e.response.reason} para el ID {product_id}'
        }, status=e.response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'success': False, 'error': f'Error de conexión con la API: {str(e)}'}, status=500)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado en el servidor: {str(e)}'}, status=500)


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
