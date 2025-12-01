#!/usr/bin/env python
"""
Script de prueba end-to-end: Simula cliente HTTP que crea un docente,
intenta login con credenciales de admin, y accede al dashboard.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from usuarios.models import Usuario
from usuarios.admin import UsuarioAdminForm

print("=" * 70)
print("PRUEBA END-TO-END: Login docente + Dashboard")
print("=" * 70)

# Limpiar usuario de prueba anterior
test_username = 'docente_e2e_test'
Usuario.objects.filter(username=test_username).delete()
print(f"\n[1] Usuario de prueba anterior eliminado si existía.")

# Crear docente con contraseña via admin form (simulado)
test_password = 'TestPassword123!'
from django.utils import timezone
form_data = {
    'username': test_username,
    'email': 'docente_e2e@test.com',
    'numero_control': 'E2E-TEST-001',
    'es_docente': True,
    'es_alumno': False,
    'es_admin_creditos': False,
    'is_staff': False,
    'is_superuser': False,
    'is_active': True,
    'raw_password': test_password,
    'password': '',
    'first_name': 'Docente',
    'last_name': 'Prueba E2E',
    'date_joined': timezone.now().isoformat(),
    'last_login': '',
}

form = UsuarioAdminForm(data=form_data)
if form.is_valid():
    user = form.save(commit=False)
    user.is_active = True
    user.save()
    print(f"[2] Docente creado: '{user.username}' ✓")
else:
    print(f"[2] ERROR: Formulario no válido:")
    for field, errors in form.errors.items():
        for error in errors:
            print(f"    {field}: {error}")
    sys.exit(1)

# Crear cliente HTTP de prueba
client = Client()
print(f"\n[3] Cliente HTTP inicializado.")

# Intentar login
print(f"\n[4] Intentando login con usuario='{test_username}', password='{test_password}'...")
login_response = client.post('/login/', {
    'username': test_username,
    'password': test_password,
})

if login_response.status_code == 302:  # Redirect on successful login
    print(f"    POST /login/ -> {login_response.status_code} (redirect) ✓")
    # Verificar que la sesión tiene user
    if 'user' in client.session and client.session['user'] is not None:
        print(f"    Usuario en sesión: {client.session.get('_auth_user_id')}")
else:
    print(f"    POST /login/ -> {login_response.status_code} (esperado 302)")
    print(f"    Response content: {login_response.content[:200]}")

# Acceder al dashboard docente
print(f"\n[5] Accediendo a /creditos/docente/dashboard/...")
dashboard_response = client.get('/creditos/docente/dashboard/')

if dashboard_response.status_code == 200:
    print(f"    GET /creditos/docente/dashboard/ -> {dashboard_response.status_code} ✓")
    if 'Panel del Docente' in str(dashboard_response.content):
        print(f"    Contenido: Dashboard encontrado en respuesta ✓")
    else:
        print(f"    Aviso: 'Panel del Docente' no encontrado en respuesta")
elif dashboard_response.status_code == 302:
    print(f"    GET /creditos/docente/dashboard/ -> {dashboard_response.status_code} (redirect a login)")
    print(f"    El usuario no está autenticado. Verifica login.")
else:
    print(f"    GET /creditos/docente/dashboard/ -> {dashboard_response.status_code} (inesperado)")

print("\n" + "=" * 70)
print("✓ PRUEBA END-TO-END COMPLETADA")
print("=" * 70)
