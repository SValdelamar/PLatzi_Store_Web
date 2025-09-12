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
    

# views.py

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import requests
import json
from django.shortcuts import redirect
from django.contrib import messages

# ... (otras vistas)

def crear_producto_view_form(request):
    """
    Esta vista obtiene las categorías de la API y renderiza
    el formulario para crear un nuevo producto con una lista desplegable.
    """
    try:
        # Obtener la lista de categorías desde la API
        response = requests.get("https://api.escuelajs.co/api/v1/categories", timeout=10)
        response.raise_for_status()
        categorias = response.json()
        
        # Filtramos las categorías para asegurarnos de que solo tengan 'id' y 'name'
        categorias_limpias = [
            {'id': cat['id'], 'name': cat['name']}
            for cat in categorias
        ]

        return render(request, "crear_producto.html", {'categorias': categorias_limpias})

    except requests.exceptions.RequestException as e:
        # Si hay un error de conexión, renderizar el formulario sin categorías y mostrar un mensaje
        messages.error(request, f"No se pudieron cargar las categorías desde la API. Por favor, inténtelo de nuevo más tarde. Error: {e}")
        return render(request, "crear_producto.html", {'categorias': []})
    except Exception as e:
        messages.error(request, f"Ocurrió un error inesperado: {str(e)}")
        return render(request, "crear_producto.html", {'categorias': []})

# La vista crear_producto (para la API) se mantiene igual,
# pero ahora recibirá un categoryId en lugar de una categoría
@require_http_methods(["POST"])
def crear_producto(request):
    """
    Maneja la petición POST de creación de un nuevo producto.
    """
    try:
        data = json.loads(request.body)
        nombre = data.get("nombre")
        precio = data.get("precio")
        descripcion = data.get("descripcion")
        # Ahora esperamos un categoryId
        categoria_id = data.get("categoriaId")
        imagen_url = data.get("imagen")
        
        # Validación de campos requeridos
        if not all([nombre, precio, descripcion, categoria_id, imagen_url]):
            return JsonResponse({'success': False, 'error': 'Todos los campos son requeridos'}, status=400)
        
        productos_data = {
            "title": nombre,
            "price": float(precio),
            "description": descripcion,
            "categoryId": int(categoria_id),  # Aseguramos que sea un entero
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


# ... (otras importaciones y vistas)

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
        
        # Realizar la petición PUT a la API
        subir_respuesta = requests.put(f"{base_url}products/{product_id}", json=productos_data, timeout=10)
        
        # Lanza una excepción para códigos de error 4xx/5xx
        subir_respuesta.raise_for_status()

        if subir_respuesta.status_code == 200:
            return JsonResponse({'success': True, 'data': subir_respuesta.json()})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato de datos JSON no válido.'}, status=400)
    
    except requests.exceptions.HTTPError as e:
        # Captura errores HTTP específicos y devuelve un mensaje claro
        return JsonResponse({
            'success': False,
            'error': f'Error en la API: {e.response.status_code} - {e.response.reason} para el ID {product_id}'
        }, status=e.response.status_code)
        
    except requests.exceptions.RequestException as e:
        # Captura otros errores de conexión
        return JsonResponse({'success': False, 'error': f'Error de conexión con la API: {str(e)}'}, status=500)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Ocurrió un error inesperado en el servidor: {str(e)}'}, status=500)

# ... (otras vistas)


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