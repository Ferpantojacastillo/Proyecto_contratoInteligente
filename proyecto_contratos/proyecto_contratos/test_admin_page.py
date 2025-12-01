#!/usr/bin/env python
"""
Script para verificar que la página de admin de crear usuario carga sin error FieldError.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 70)
print("PRUEBA: Cargar página admin de crear usuario")
print("=" * 70)

# Crear un superuser para poder acceder al admin
superuser_username = 'admin_test'
User.objects.filter(username=superuser_username).delete()

superuser = User.objects.create_superuser(
    username=superuser_username,
    email='admin@test.com',
    password='AdminPassword123!'
)
print(f"\n[1] Superuser creado: '{superuser.username}'")

# Crear cliente y hacer login al admin
client = Client()
login_response = client.post('/admin/login/', {
    'username': superuser_username,
    'password': 'AdminPassword123!',
    'next': '/admin/',
}, follow=True)

print(f"[2] Login en admin: {login_response.status_code}")

# Intentar acceder a la página de crear usuario
print(f"\n[3] GET /admin/usuarios/usuario/add/...")
add_user_response = client.get('/admin/usuarios/usuario/add/')

print(f"    Status code: {add_user_response.status_code}")

if add_user_response.status_code == 200:
    print(f"    ✓ Página cargada exitosamente")
    # Buscar si aparece el campo raw_password
    if 'raw_password' in str(add_user_response.content):
        print(f"    ✓ Campo 'raw_password' encontrado en formulario")
    else:
        print(f"    ⚠ Campo 'raw_password' NO encontrado (podría estar con otro nombre)")
    if 'Contraseña' in str(add_user_response.content):
        print(f"    ✓ Texto 'Contraseña' encontrado")
else:
    print(f"    ✗ Error: {add_user_response.status_code}")
    # Imprimir primeras 500 chars de la respuesta si es error
    content_preview = str(add_user_response.content)[:500]
    print(f"    Response preview: {content_preview}")

print("\n" + "=" * 70)
print("✓ PRUEBA DE ADMIN COMPLETADA")
print("=" * 70)
