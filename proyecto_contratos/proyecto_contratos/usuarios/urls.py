from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('docente/registro/', views.docente_registro, name='docente_registro'),
    path('docente/credenciales/', views.docente_credenciales, name='docente_credenciales'),
    path('docente/login/', views.login_view, name='docente_login'),
    path('perfil/', views.perfil, name='perfil'),
]








  

