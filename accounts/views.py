from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

# Vista para mostrar y procesar el login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}")
            return redirect('products:products')  # Redirige a la página principal de productos
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')


# Vista para mostrar y procesar el registro
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validar contraseñas
        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('accounts:register')

        # Validar que el usuario no exista
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso")
            return redirect('accounts:register')

        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Iniciar sesión automáticamente
        login(request, user)
        messages.success(request, "Registro exitoso, ¡Bienvenido!")

        # Redirigir a inicio de productos
        return redirect('products:products')

    return render(request, 'accounts/register.html')


# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente")
    return redirect('accounts:login')
