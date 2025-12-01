#!/usr/bin/env python
"""
Script de prueba para verificar que las contraseñas asignadas por admin funcionan.
Simula el flujo: crear docente con contraseña via admin form, luego autenticar.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import authenticate
from usuarios.models import Usuario
from usuarios.admin import UsuarioAdminForm

print("=" * 70)
print("PRUEBA: Contraseña asignada por admin")
print("=" * 70)

# 1. Limpiar usuarios de prueba anteriores
test_username = 'docente_prueba_admin_test'
Usuario.objects.filter(username=test_username).delete()
print(f"\n[1] Limpiado usuario anterior '{test_username}' si existía.")

# 2. Simular formulario de admin con contraseña proporcionada
from django.utils import timezone
test_password = 'MiContraseña123!'
form_data = {
    'username': test_username,
    'email': 'docente_prueba@test.com',
    'numero_control': 'NC-999-TEST',
    'es_docente': True,
    'es_alumno': False,
    'es_admin_creditos': False,
    'is_staff': False,
    'is_superuser': False,
    'is_active': True,
    'raw_password': test_password,
    'password': '',  # Campo de modelo, vacío (se llenará via raw_password)
    'first_name': '',
    'last_name': '',
    'date_joined': timezone.now().isoformat(),
    'last_login': '',
}

form = UsuarioAdminForm(data=form_data)
if form.is_valid():
    print(f"\n[2] Formulario admin válido ✓")
    user = form.save(commit=False)
    user.is_active = True
    user.save()
    print(f"    Usuario creado: '{user.username}' (is_active={user.is_active})")
else:
    print(f"\n[2] ERROR: Formulario no válido:")
    for field, errors in form.errors.items():
        for error in errors:
            print(f"    {field}: {error}")
    sys.exit(1)

# 3. Verificar que la contraseña se guardó correctamente
user_from_db = Usuario.objects.get(username=test_username)
print(f"\n[3] Verificación en BD:")
print(f"    is_active: {user_from_db.is_active}")
print(f"    password hash (primeros 20 chars): {user_from_db.password[:20]}...")

# 4. Test check_password (verifica que el hash sea correcto)
if user_from_db.check_password(test_password):
    print(f"    check_password('{test_password}'): ✓ TRUE")
else:
    print(f"    check_password('{test_password}'): ✗ FALSE")
    print("    ERROR: El hash no corresponde a la contraseña.")
    sys.exit(1)

# 5. Test authenticate (simula lo que hace Django en login)
auth_user = authenticate(username=test_username, password=test_password)
if auth_user is not None:
    print(f"\n[4] authenticate() result: ✓ LOGIN CORRECTO")
    print(f"    Usuario autenticado: {auth_user.username}")
    print(f"    es_docente: {auth_user.es_docente}")
else:
    print(f"\n[4] authenticate() result: ✗ LOGIN FALLIDO")
    print(f"    Django no puede autenticar con usuario='{test_username}', pass='{test_password}'")
    sys.exit(1)

# 6. Prueba con contraseña incorrecta (debe fallar)
auth_wrong = authenticate(username=test_username, password='ContraseñaIncorrecta')
if auth_wrong is None:
    print(f"\n[5] Seguridad: authenticate() con contraseña incorrecta: ✓ Rechazada (correcto)")
else:
    print(f"\n[5] Seguridad: authenticate() con contraseña incorrecta: ✗ Se aceptó (ERROR)")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ TODAS LAS PRUEBAS PASARON - EL FLUJO DE ADMIN FUNCIONA CORRECTAMENTE")
print("=" * 70)
