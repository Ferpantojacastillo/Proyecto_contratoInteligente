#!/usr/bin/env python
import os,sys,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','proyecto_creditos.settings')
proj = r'c:\Users\fpant\Documents\GitHub\Proyecto_contratoInteligente\proyecto_contratos\proyecto_contratos'
sys.path.insert(0, proj)
django.setup()
from django.test import Client
from usuarios.models import Usuario
from actividades.models import Actividad
from creditos.models import Credito
from django.utils import timezone

# cleanup
Usuario = Usuario
Usuario.objects.filter(username__startswith='e2e_alum_').delete()
Actividad.objects.filter(nombre__startswith='E2E Actividad').delete()
Credito.objects.filter(nombre__startswith='E2E Actividad').delete()

# create alumno
al = Usuario.objects.create_user(username='e2e_alum_1', password='Test12345', es_alumno=True, is_active=True, numero_control='E2E-001')
print('Alumno creado:', al.username)
# create actividad
act = Actividad.objects.create(nombre='E2E Actividad Demo', tipo='academico', fecha=timezone.now(), creado_por=None)
print('Actividad creada:', act.id)

client = Client()
client.login(username='e2e_alum_1', password='Test12345')
# GET detalle
resp1 = client.get(f'/actividades/{act.id}/')
print('GET detalle status', resp1.status_code)
# POST firmar (without inscribir)
resp2 = client.post(f'/actividades/{act.id}/firmar/', {})
print('POST firmar status', resp2.status_code)
# check credit
c = Credito.objects.filter(nombre__icontains='E2E Actividad').first()
print('Credito created?', bool(c), c and {'id': c.id, 'liberado': c.liberado, 'firmado_alumno': c.firmado_alumno, 'alumno': getattr(c.alumno,'username',None)})

# now check mis_creditos
resp3 = client.get('/creditos/mis_creditos/')
print('mis_creditos status', resp3.status_code)
print('Contains E2E Actividad', 'E2E Actividad' in resp3.content.decode('utf-8'))
