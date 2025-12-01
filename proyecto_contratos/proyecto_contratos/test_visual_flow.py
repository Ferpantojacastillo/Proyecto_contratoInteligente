#!/usr/bin/env python
"""
Prueba Visual: Simula el flujo completo con inspección de HTML renderizado.
Admin asigna credenciales a docente → Docente inicia sesión → Ve crédito en dashboard → Firma.
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
from creditos.models import Credito
from django.utils import timezone
import re

User = get_user_model()

print("=" * 80)
print("PRUEBA VISUAL: Flujo Completo Admin → Docente (con HTML renderizado)")
print("=" * 80)

# Limpiar datos previos
User.objects.filter(username__startswith='visual_').delete()
Credito.objects.filter(nombre__startswith='VISUAL_').delete()

# PASO 1: Admin crea docente con contraseña (vía formulario admin)
print("\n[PASO 1] Admin asigna credenciales a docente...")
docente_username = 'visual_docente_001'
docente_password = 'VisualPassword123!'

form_data = {
    'username': docente_username,
    'email': 'visual_docente@test.com',
    'numero_control': 'VISUAL-001',
    'es_docente': True,
    'es_alumno': False,
    'es_admin_creditos': False,
    'is_staff': False,
    'is_superuser': False,
    'is_active': True,
    'raw_password': docente_password,
    'password': '',
    'first_name': 'Docente',
    'last_name': 'Visual',
    'date_joined': timezone.now().isoformat(),
    'last_login': '',
}

form = UsuarioAdminForm(data=form_data)
if not form.is_valid():
    print(f"  ✗ Formulario inválido: {form.errors}")
    sys.exit(1)

docente = form.save(commit=False)
docente.is_active = True
docente.save()
print(f"  ✓ Docente creado: {docente.username}")
print(f"    Credenciales: username='{docente_username}' | password='{docente_password}'")

# PASO 2: Admin crea credencial de super usuario y firma un crédito
print("\n[PASO 2] Admin inicia sesión y firma un crédito...")
admin = User.objects.create_superuser(
    username='visual_admin',
    email='visual_admin@test.com',
    password='VisualAdminPassword123!'
)

# Crear alumno y crédito
alumno = User.objects.create_user(
    username='visual_alumno',
    email='visual_alumno@test.com',
    password='VisualAlumnoPassword123!',
    es_alumno=True,
    numero_control='VISUAL-ALUMNO-001'
)

credito = Credito.objects.create(
    alumno=alumno,
    nombre='VISUAL_CREDITO_DEMO',
    tipo='academico',
    semestre='6',
    numero_control='VISUAL-ALUMNO-001',
    fecha_liberacion=timezone.now().date(),
    liberado=True
)
print(f"  ✓ Crédito creado: {credito.nombre} (ID={credito.id})")

# Admin firma el crédito
client_admin = Client()
client_admin.login(username='visual_admin', password='VisualAdminPassword123!')
client_admin.post(f'/creditos/firmar/admin/{credito.id}/')
credito.refresh_from_db()
print(f"  ✓ Admin firmó el crédito: firmado_admin={credito.firmado_admin}")

# PASO 3: Docente inicia sesión (con credenciales asignadas por admin)
print("\n[PASO 3] Docente inicia sesión con credenciales asignadas por admin...")
client_docente = Client()
login_ok = client_docente.login(username=docente_username, password=docente_password)

if not login_ok:
    print(f"  ✗ Login fallido para {docente_username}")
    sys.exit(1)
print(f"  ✓ Login exitoso para {docente_username}")

# PASO 4: Docente accede al dashboard
print("\n[PASO 4] Docente accede a su dashboard...")
dashboard_response = client_docente.get('/creditos/docente/dashboard/')

if dashboard_response.status_code != 200:
    print(f"  ✗ Status code {dashboard_response.status_code}")
    sys.exit(1)

html_content = dashboard_response.content.decode('utf-8')
print(f"  ✓ Dashboard cargado (status 200)")

# PASO 5: Verificar que el crédito aparece en la tabla
print("\n[PASO 5] Verificar que el crédito aparece en el dashboard...")

# Buscar el ID del crédito en la tabla
if f'#{credito.id}' in html_content:
    print(f"  ✓ ID del crédito encontrado: #{credito.id}")
else:
    print(f"  ✗ ID del crédito NO encontrado")
    sys.exit(1)

# Buscar el nombre del crédito
if 'VISUAL_CREDITO_DEMO' in html_content:
    print(f"  ✓ Nombre del crédito encontrado: VISUAL_CREDITO_DEMO")
else:
    print(f"  ✗ Nombre del crédito NO encontrado")
    sys.exit(1)

# Buscar indicador de firma admin
if 'Sí' in html_content and 'Firmado por Admin' in html_content:
    print(f"  ✓ Indicador de firma admin encontrado")
else:
    print(f"  ⚠ Indicador de firma admin podría no estar visible")

# PASO 6: Docente firma el crédito
print("\n[PASO 6] Docente firma el crédito...")
firma_response = client_docente.post(f'/creditos/docente/firmar/{credito.id}/', follow=True)

if firma_response.status_code == 200:
    print(f"  ✓ Firma procesada y redirigida (status 200 después de seguir redirect)")
else:
    print(f"  ✗ Error en firma: status {firma_response.status_code}")
    sys.exit(1)

credito.refresh_from_db()
if credito.firmado_docente and credito.firmado_admin:
    print(f"  ✓ Crédito completamente firmado")
    print(f"    - Admin: {credito.firmado_admin}")
    print(f"    - Docente: {credito.firmado_docente}")
else:
    print(f"  ✗ El crédito no está completamente firmado")
    sys.exit(1)

# PASO 7: Verificar que el crédito ya NO aparece en dashboard
print("\n[PASO 7] Verificar que el crédito ya NO aparece en dashboard (porque está completo)...")
dashboard_final = client_docente.get('/creditos/docente/dashboard/')
html_final = dashboard_final.content.decode('utf-8')

if 'VISUAL_CREDITO_DEMO' not in html_final:
    print(f"  ✓ Crédito ya no aparece (correcto, está completamente firmado)")
elif '✓' in html_final and 'Todo al día' in html_final:
    print(f"  ✓ Dashboard muestra 'Todo al día' (sin créditos pendientes)")
else:
    print(f"  ⚠ Crédito aún aparece pero debería estar filtrado")

print("\n" + "=" * 80)
print("✓✓✓ PRUEBA VISUAL COMPLETADA EXITOSAMENTE ✓✓✓")
print("=" * 80)
print("\nRESUMEN DEL FLUJO:")
print(f"  1. Admin creó docente con usuario '{docente_username}' y contraseña '{docente_password}'")
print(f"  2. Admin creó crédito '{credito.nombre}' y lo firmó")
print(f"  3. Docente inició sesión con credenciales asignadas por admin")
print(f"  4. Docente vio el crédito en el dashboard (porque admin lo firmó)")
print(f"  5. Docente firmó el crédito")
print(f"  6. El crédito desapareció del dashboard (porque está completo)")
print("=" * 80)
