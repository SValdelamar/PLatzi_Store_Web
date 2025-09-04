from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import json
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.shortcuts import redirect

def inicio(request):
    """
    Esta vista renderiza la plantilla de inicio.
    """
    return render(request, "inicio.html")


def porducts_views(request):
    """
    Esta vista obtiene los productos de la API y los pasa a la plantilla.
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
    Esta vista renderiza el formulario para crear un nuevo producto.
    """
    return render(request, "crear_producto.html")

@csrf_exempt
@require_http_methods(["POST"])


def crear_producto(request):
    """
    Esta vista actúa como un endpoint de API para manejar la petición POST
    de creación de un nuevo producto.
    """
    try:
        # Cargar los datos JSON del cuerpo de la petición
        data = json.loads(request.body)
        nombre = data.get("nombre")
        precio = data.get("precio")
        descripcion = data.get("descripcion")
        imagen_url = data.get("imagen")
        
        if not all([nombre, precio, descripcion, imagen_url]):
            return JsonResponse({'success': False, 'error': 'Todos los campos son requeridos'}, status=400)
        
        base_url = "https://api.escuelajs.co/api/v1/"
        
        # Corregir la estructura de los datos que se envían a la API
        productos_data = {
            "title": nombre,
            "price": float(precio),
            "description": descripcion,
            "categoryId": 1,
            "images": [imagen_url],
        }
        
        # Realizar la petición POST a la API
        subir_respuesta = requests.post(f"{base_url}products/", json=productos_data, timeout=10)
        subir_respuesta.raise_for_status()  # Lanzará una excepción para códigos de error 4xx/5xx
        
        if subir_respuesta.status_code == 201:
            datos = subir_respuesta.json()
            return JsonResponse({'success': True, 'data': datos})
        else:
            return JsonResponse({
                'success': False,
                'error': f'Error en la API: {subir_respuesta.status_code} - {subir_respuesta.text}'
            }, status=subir_respuesta.status_code)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato de datos JSON no válido.'}, status=400)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'success': False, 'error': f'Error de conexión con la API: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)
    
def editar_producto_form(request, product_id):
    """
    Renderiza el formulario de edición de un producto.
    Obtiene los datos del producto de la API para pre-llenar el formulario.
    """
    try:
        response = requests.get(f"https://api.escuelajs.co/api/v1/products/{product_id}")
        response.raise_for_status()  # Lanza una excepción para errores 4xx/5xx
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
    Endpoint de la API para manejar la petición PUT de actualización de un producto.
    """
    try:
        data = json.loads(request.body)
        title = data.get("title")
        price = data.get("price")
        description = data.get("description")

        if not all([title, price, description]):
            return JsonResponse({'success': False, 'error': 'Título, precio y descripción son requeridos.'}, status=400)

        productos_data = {
            "title": title,
            "price": float(price),
            "description": description,
        }

        base_url = "https://api.escuelajs.co/api/v1/"
        subir_respuesta = requests.put(f"{base_url}products/{product_id}", json=productos_data, timeout=10)
        subir_respuesta.raise_for_status()

        if subir_respuesta.status_code == 200:
            return JsonResponse({'success': True, 'data': subir_respuesta.json()})
        else:
            return JsonResponse({
                'success': False,
                'error': f'Error en la API: {subir_respuesta.status_code} - {subir_respuesta.text}'
            }, status=subir_respuesta.status_code)

    except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
        return JsonResponse({'success': False, 'error': f'Ocurrió un error: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def eliminar_producto(request, product_id):
    """
    Maneja la petición POST para eliminar un producto.
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


    
    
