"""
URL configuration for proyecto_creditos project.

The `urlpatterns` list routes URLs to views. 
For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('usuarios/', include('usuarios.urls')),
    path('creditos/', include('creditos.urls')),
    path('actividades/', include('actividades.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







