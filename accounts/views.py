from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserSerializer
from django.shortcuts import render, redirect
from django.contrib import messages



def login_view(request):
    # Simplemente renderiza el formulario
    return render(request, 'accounts/login.html')

def register_view(request):
    # Simplemente renderiza el formulario
    return render(request, 'accounts/register.html')


# Vista para cerrar sesión
@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'success': True, 'message': 'Usuario registrado', 'user': UserSerializer(user).data, 'token': token.key}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'message': 'Error en registro', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'success': False, 'message': 'Debe enviar username y password'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'success': True, 'message': 'Autenticación satisfactoria', 'user': UserSerializer(user).data, 'token': token.key}, status=status.HTTP_200_OK)
    return Response({'success': False, 'message': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
    Endpoint API para cerrar sesión usando token.
    """
    try:
        # Eliminamos el token del usuario
        request.user.auth_token.delete()
    except Token.DoesNotExist:
        return Response({"success": False, "message": "Token no encontrado"}, status=400)

    # Cierra la sesión en Django
    logout(request)
    return Response({"success": True, "message": "Sesión cerrada correctamente"})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile_api(request):
    user = request.user
    return Response({'success': True, 'user': UserSerializer(user).data}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_username_api(request):
    username = request.GET.get('username', '')
    if not username:
        return Response({'success': False, 'message': 'Debe enviar un username'}, status=400)
    exists = User.objects.filter(username=username).exists()
    return Response({'success': True, 'available': not exists}, status=200)
