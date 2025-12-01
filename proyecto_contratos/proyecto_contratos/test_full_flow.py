#!/usr/bin/env python
"""
Prueba completa: crear docente via admin form (simulado), login, y acceder al dashboard.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from usuarios.admin import UsuarioAdminForm
from django.utils import timezone

User = get_user_model()

print("=" * 70)
print("PRUEBA COMPLETA: Admin → Form → Login → Dashboard")
print("=" * 70)

# Limpiar usuarios de prueba
test_docente = 'docente_final_test'
User.objects.filter(username=test_docente).delete()
print(f"\n[1] Usuario de prueba limpiado.")

# PASO 1: Crear admin form y docente
test_password = 'DocPassword123!'
form_data = {
    'username': test_docente,
    'email': 'docente_final@test.com',
    'numero_control': 'DOC-FINAL-001',
    'es_docente': True,
    'es_alumno': False,
    'es_admin_creditos': False,
    'is_staff': False,
    'is_superuser': False,
    'is_active': True,
    'raw_password': test_password,
    'password': '',
    'first_name': 'DocFinal',
    'last_name': 'Test',
    'date_joined': timezone.now().isoformat(),
    'last_login': '',
}

form = UsuarioAdminForm(data=form_data)
if form.is_valid():
    user = form.save(commit=False)
    user.is_active = True
    user.save()
    print(f"\n[2] Docente creado via admin form:")
    print(f"    username: {user.username}")
    print(f"    es_docente: {user.es_docente}")
    print(f"    is_active: {user.is_active}")
    print(f"    password hash: {user.password[:30]}...")
else:
    print(f"\n[2] ERROR: Formulario no válido:")
    for field, errors in form.errors.items():
        for error in errors:
            print(f"    {field}: {error}")
    sys.exit(1)

# PASO 2: Verificar que la contraseña se guardó correctamente
user_check = User.objects.get(username=test_docente)
if user_check.check_password(test_password):
    print(f"\n[3] Verificación de contraseña: ✓ check_password() = True")
else:
    print(f"\n[3] Verificación de contraseña: ✗ FALLO")
    sys.exit(1)

# PASO 3: Client HTTP - login
client = Client()
print(f"\n[4] Cliente HTTP inicializado.")

login_response = client.post('/login/', {
    'username': test_docente,
    'password': test_password,
})

if login_response.status_code == 302:
    print(f"    POST /login/ -> {login_response.status_code} (redirect) ✓")
else:
    print(f"    POST /login/ -> {login_response.status_code} (esperado 302)")
    print(f"    Content: {login_response.content[:300]}")
    sys.exit(1)

# PASO 4: Acceder al dashboard docente
dashboard_response = client.get('/creditos/docente/dashboard/')

if dashboard_response.status_code == 200:
    print(f"\n[5] GET /creditos/docente/dashboard/ -> 200 ✓")
    content = str(dashboard_response.content)
    if 'Panel del Docente' in content:
        print(f"    'Panel del Docente' encontrado en respuesta ✓")
    if 'Actividades' in content:
        print(f"    'Actividades' encontrado en respuesta ✓")
else:
    print(f"\n[5] GET /creditos/docente/dashboard/ -> {dashboard_response.status_code}")
    if dashboard_response.status_code == 302:
        print(f"    El usuario no está autenticado (redirect)")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ PRUEBA COMPLETA EXITOSA - FLUJO FUNCIONA DE PRINCIPIO A FIN")
print("=" * 70)
