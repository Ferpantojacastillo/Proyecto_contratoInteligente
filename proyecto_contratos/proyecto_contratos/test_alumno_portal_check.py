#!/usr/bin/env python
"""
Verifica que el portal de alumno muestra el botón de firmar correctamente.
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
User.objects.filter(username__startswith='portal_alum_').delete()
Credito.objects.filter(nombre__startswith='PORTALALUM_').delete()

# Crear alumno
al = User.objects.create_user(username='portal_alum_1', password='AlumPass123!', es_alumno=True, is_active=True, numero_control='ALUM-001')
print('Alumno creado:', al.username, al.numero_control)

# Crear credito liberado sin asignar pero con numero_control igual al alumno
cred = Credito.objects.create(alumno=None, nombre='PORTALALUM_CREDIT', tipo='academico', semestre='1', numero_control='ALUM-001', liberado=True)
print('Crédito creado:', cred.id, cred.nombre, 'liberado=', cred.liberado, 'alumno=', cred.alumno)

client = Client()
login_ok = client.login(username='portal_alum_1', password='AlumPass123!')
print('Login alumno OK?', login_ok)

resp = client.get('/creditos/mis_creditos/')
print('/creditos/mis_creditos/ status:', resp.status_code)
content = resp.content.decode('utf-8')
print('Contains PORTALALUM_CREDIT?', 'PORTALALUM_CREDIT' in content)
print('Contains Firmar (Alumno)?', 'Firmar (Alumno)' in content)
print('\n--- snippet ---\n', content.split('\n')[:80])
