#!/usr/bin/env python
"""
Verifica que el portal de docente muestra créditos para asignar y firmar.
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from creditos.models import Credito
from django.utils import timezone

User = get_user_model()

# Limpiar pruebas previas
User.objects.filter(username__startswith='portal_check_').delete()
Credito.objects.filter(nombre__startswith='PORTALCHECK_').delete()

# Crear docente
doc = User.objects.create_user(username='portal_check_doc', password='DocPass123!', es_docente=True, is_active=True)
print('Docente creado:', doc.username)

# Crear credito no liberado (para que aparezca en "Asignar créditos")
cred1 = Credito.objects.create(alumno=None, nombre='PORTALCHECK_CREDIT_1', tipo='academico', semestre='1', numero_control='', liberado=False)
print('Crédito creado (no liberado):', cred1.id)

# Crear credito liberado but not signed (should appear in dashboard to sign)
# But per new flow, docente dashboard shows liberado=True and firmado_docente=False
cred2 = Credito.objects.create(alumno=None, nombre='PORTALCHECK_CREDIT_2', tipo='academico', semestre='1', numero_control='', liberado=True)
print('Crédito creado (liberado):', cred2.id)

client = Client()
login_ok = client.login(username='portal_check_doc', password='DocPass123!')
print('Login docente OK?', login_ok)

resp_asignar = client.get('/creditos/docente/asignar/')
print('/creditos/docente/asignar/ status:', resp_asignar.status_code)
print('Contains PORTALCHECK_CREDIT_1?', 'PORTALCHECK_CREDIT_1' in resp_asignar.content.decode('utf-8'))

resp_dashboard = client.get('/creditos/docente/dashboard/')
print('/creditos/docente/dashboard/ status:', resp_dashboard.status_code)
print('Contains PORTALCHECK_CREDIT_2?', 'PORTALCHECK_CREDIT_2' in resp_dashboard.content.decode('utf-8'))

print('--- Response snippets ---')
print('/asignar snippet:', resp_asignar.content.decode('utf-8')[:500])
print('/dashboard snippet:', resp_dashboard.content.decode('utf-8')[:500])
