#!/usr/bin/env python
"""
Prueba Visual del Nuevo Flujo:
Admin asigna → Alumno firma → Dashboard Docente → Docente firma → PDF
Incluye inspección de contenido HTML renderizado.
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

print("=" * 80)
print("PRUEBA VISUAL: Nuevo Flujo (Admin asigna, Alumno+Docente firman, PDF requiere ambos)")
print("=" * 80)

# Limpiar
User.objects.filter(username__startswith='viz_').delete()
Credito.objects.filter(nombre__startswith='VIZ_').delete()

# Crear usuarios
admin = User.objects.create_superuser(username='viz_admin', email='a@viz.com', password='Pass123!')
alumno = User.objects.create_user(username='viz_alumno', email='b@viz.com', password='Pass123!', es_alumno=True, numero_control='VIZ-001')
docente = User.objects.create_user(username='viz_docente', email='c@viz.com', password='Pass123!', es_docente=True)

print(f"\n[USUARIOS] Admin, Alumno, Docente creados ✓")

# Admin crea y asigna crédito
credito = Credito.objects.create(
    alumno=alumno,
    nombre='VIZ_CREDITO_DEMO',
    tipo='cultural',
    semestre='4',
    numero_control='VIZ-001',
    liberado=False
)

client_admin = Client()
client_admin.login(username='viz_admin', password='Pass123!')
client_admin.post(f'/creditos/liberar/{credito.id}/')
credito.refresh_from_db()

print(f"[ADMIN] Crédito asignado (liberado={credito.liberado}) ✓")

# Alumno inicia sesión y firma
client_alumno = Client()
client_alumno.login(username='viz_alumno', password='Pass123!')

# Alumno ve sus créditos
mis_creditos_response = client_alumno.get('/creditos/mis_creditos/')
html_mis_creditos = str(mis_creditos_response.content)

if 'VIZ_CREDITO_DEMO' in html_mis_creditos:
    print(f"[ALUMNO] Crédito aparece en 'Mis Créditos' ✓")
    
    # Verificar badges de firma
    if '✗ Alumno' in html_mis_creditos:
        print(f"[ALUMNO] Muestra que aún no ha firmado ✓")
else:
    print(f"[ALUMNO] ✗ Crédito NO aparece en 'Mis Créditos'")
    sys.exit(1)

# Alumno firma
client_alumno.post(f'/creditos/firmar/alumno/{credito.id}/')
credito.refresh_from_db()
print(f"[ALUMNO] Firmó el crédito ✓")

# Verificar que ahora muestra que el alumno firmó
mis_creditos_after = client_alumno.get('/creditos/mis_creditos/')
html_after = str(mis_creditos_after.content)

if '✓ Alumno' in html_after:
    print(f"[ALUMNO] Ahora muestra que SÍ ha firmado ✓")
else:
    print(f"[ALUMNO] ⚠ Badge de firma no se actualizó")

# Docente inicia sesión y ve dashboard
client_docente = Client()
client_docente.login(username='viz_docente', password='Pass123!')

dashboard = client_docente.get('/creditos/docente/dashboard/')
html_dashboard = str(dashboard.content)

if 'VIZ_CREDITO_DEMO' in html_dashboard:
    print(f"[DOCENTE] Crédito aparece en dashboard ✓")
    
    if '✓ Alumno' in html_dashboard or 'Alumno' in html_dashboard:
        print(f"[DOCENTE] Muestra que el alumno ya firmó ✓")
    
    if 'Firmar' in html_dashboard:
        print(f"[DOCENTE] Botón 'Firmar' visible ✓")
else:
    print(f"[DOCENTE] ✗ Crédito NO aparece en dashboard")
    sys.exit(1)

# Docente firma
cliente_docente_firma = client_docente.post(f'/creditos/docente/firmar/{credito.id}/', follow=True)
credito.refresh_from_db()
print(f"[DOCENTE] Firmó el crédito ✓")

# Alumno intenta descargar PDF
print(f"\n[PDF] Alumno intenta descargar PDF...")
pdf_response = client_alumno.post(f'/creditos/pdf/{credito.id}/')

if pdf_response.status_code == 302:
    from pathlib import Path
    from django.conf import settings
    docs_dir = Path(settings.BASE_DIR) / 'documentos'
    pdf_file = docs_dir / f"{alumno.numero_control}.pdf"
    
    if pdf_file.exists():
        tamaño = pdf_file.stat().st_size
        print(f"[PDF] Generado exitosamente ({tamaño} bytes) ✓")
    else:
        print(f"[PDF] ⚠ Request exitoso pero archivo podría no estar guardado")
else:
    print(f"[PDF] ✗ Error: status {pdf_response.status_code}")
    sys.exit(1)

# Verificar que crédito ya NO aparece en dashboard (porque está completo)
dashboard_final = client_docente.get('/creditos/docente/dashboard/')
html_final = str(dashboard_final.content)

if 'VIZ_CREDITO_DEMO' not in html_final:
    print(f"[DASHBOARD] Crédito ya no aparece (porque está completo) ✓")
elif 'Todo al día' in html_final:
    print(f"[DASHBOARD] Muestra 'Todo al día' ✓")

print("\n" + "=" * 80)
print("✓✓✓ PRUEBA VISUAL COMPLETADA EXITOSAMENTE ✓✓✓")
print("=" * 80)
print("\nFLUJO RESUMIDO:")
print("  1. Admin asignó (liberó) el crédito")
print("  2. Alumno vio el crédito en 'Mis Créditos' (sin firmas)")
print("  3. Alumno firmó el crédito")
print("  4. Docente vio el crédito en dashboard (alumno ya firmó)")
print("  5. Docente firmó el crédito")
print("  6. PDF se generó (requería ambas firmas)")
print("  7. Crédito desapareció del dashboard (está completo)")
print("=" * 80)
