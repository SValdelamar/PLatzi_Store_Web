from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_api, name='api_register'),
    path('login/', views.login_api, name='api_login'),
    path('logout/', views.logout_api, name='api_logout'),
    path('profile/', views.profile_api, name='api_profile'),  # <-- aquí el cambio
    path('check-username/', views.check_username_api, name='api_check_username'),
    path('login-form/', views.login_view, name='login_form'),
    path('register-form/', views.register_view, name='register_form'),

]
