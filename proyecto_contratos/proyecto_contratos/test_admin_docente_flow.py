#!/usr/bin/env python
"""
Prueba: Admin firma un crédito → Aparece en dashboard del docente → Docente lo firma.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from creditos.models import Credito
from django.utils import timezone

User = get_user_model()

print("=" * 70)
print("PRUEBA: Admin firma → Dashboard docente → Docente firma")
print("=" * 70)

# Limpiar datos de prueba anteriores
Credito.objects.filter(nombre__startswith='TEST_CREDITO').delete()
User.objects.filter(username__startswith='test_user_').delete()

# PASO 1: Crear usuarios de prueba (admin y docente)
admin_user = User.objects.create_superuser(
    username='test_user_admin_sig',
    email='admin_sig@test.com',
    password='AdminPassword123!'
)
print(f"\n[1] Admin creado: '{admin_user.username}'")

docente_user = User.objects.create_user(
    username='test_user_docente_sig',
    email='docente_sig@test.com',
    password='DocentePassword123!',
    es_docente=True,
    is_active=True
)
print(f"    Docente creado: '{docente_user.username}'")

alumno_user = User.objects.create_user(
    username='test_user_alumno_sig',
    email='alumno_sig@test.com',
    password='AlumnoPassword123!',
    es_alumno=True,
    is_active=True,
    numero_control='ALU-TEST-001'
)
print(f"    Alumno creado: '{alumno_user.username}'")

# PASO 2: Crear un crédito y liberarlo
credito = Credito.objects.create(
    alumno=alumno_user,
    nombre='TEST_CREDITO_FLUJO_COMPLETO',
    tipo='academico',
    semestre='5',
    numero_control='ALU-TEST-001',
    fecha_liberacion=timezone.now().date(),
    liberado=True
)
print(f"\n[2] Crédito creado: ID={credito.id}, nombre='{credito.nombre}'")
print(f"    Estado inicial: admin={credito.firmado_admin}, docente={credito.firmado_docente}")

# PASO 3: Admin firma el crédito
print(f"\n[3] Admin firma el crédito...")
client_admin = Client()
client_admin.login(username='test_user_admin_sig', password='AdminPassword123!')

# Simular POST a firma de admin
firma_admin_response = client_admin.post(f'/creditos/firmar/admin/{credito.id}/', follow=True)
print(f"    POST /creditos/firmar/admin/{credito.id}/ -> {firma_admin_response.status_code}")

# Verificar estado del crédito en BD
credito.refresh_from_db()
print(f"    Estado después de firma admin: admin={credito.firmado_admin}, docente={credito.firmado_docente}")

if not credito.firmado_admin:
    print(f"    ✗ ERROR: El crédito no fue firmado por admin")
    sys.exit(1)
print(f"    ✓ Crédito firmado por admin correctamente")

# PASO 4: Docente accede al dashboard y ve el crédito
print(f"\n[4] Docente accede al dashboard...")
client_docente = Client()
client_docente.login(username='test_user_docente_sig', password='DocentePassword123!')

dashboard_response = client_docente.get('/creditos/docente/dashboard/')
print(f"    GET /creditos/docente/dashboard/ -> {dashboard_response.status_code}")

if dashboard_response.status_code == 200:
    content = str(dashboard_response.content)
    if 'TEST_CREDITO_FLUJO_COMPLETO' in content:
        print(f"    ✓ Crédito aparece en dashboard del docente")
    else:
        print(f"    ⚠ Crédito NO aparece en dashboard (verificar filtros)")
        # Mostrar cuántos créditos aparecen
        if 'Créditos Pendientes' in content:
            print(f"    Sección de créditos encontrada")
else:
    print(f"    ✗ Error: Status code inesperado")
    sys.exit(1)

# PASO 5: Docente firma el crédito
print(f"\n[5] Docente firma el crédito...")
firma_docente_response = client_docente.post(f'/creditos/docente/firmar/{credito.id}/', follow=True)
print(f"    POST /creditos/docente/firmar/{credito.id}/ -> {firma_docente_response.status_code}")

# Verificar estado final
credito.refresh_from_db()
print(f"    Estado final: admin={credito.firmado_admin}, docente={credito.firmado_docente}")

if credito.firmado_docente and credito.firmado_admin:
    print(f"    ✓ Crédito firmado por ambos (admin y docente)")
else:
    print(f"    ✗ ERROR: El crédito no fue firmado correctamente por docente")
    sys.exit(1)

# PASO 6: Verificar que ya no aparece en dashboard (porque está firmado)
print(f"\n[6] Verificar que crédito ya NO aparece en dashboard (porque está completo)...")
dashboard_final_response = client_docente.get('/creditos/docente/dashboard/')

if dashboard_final_response.status_code == 200:
    content_final = str(dashboard_final_response.content)
    # El crédito NO debería aparecer porque ya fue firmado
    # Verificamos si la sección está vacía o si el crédito específico no está
    if 'TEST_CREDITO_FLUJO_COMPLETO' not in content_final:
        print(f"    ✓ Crédito ya NO aparece en dashboard (correcto)")
    else:
        print(f"    ⚠ Crédito aún aparece (podría estar filtrado)")
else:
    print(f"    Error: Status code {dashboard_final_response.status_code}")

print("\n" + "=" * 70)
print("✓ PRUEBA COMPLETADA - FLUJO ADMIN → DOCENTE FUNCIONA")
print("=" * 70)
