#!/usr/bin/env python
import os,sys,django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','proyecto_creditos.settings')
proj = r'c:\Users\fpant\Documents\GitHub\Proyecto_contratoInteligente\proyecto_contratos\proyecto_contratos'
sys.path.insert(0, proj)
django.setup()
from django.test import Client
c = Client()
from creditos.models import Credito
cred = Credito.objects.first()
if cred:
    resp = c.get(f'/creditos/contrato/{cred.id}/')
    print('GET /creditos/contrato/{0}/ ->'.format(cred.id), resp.status_code)
    content = resp.content.decode('utf-8')
    print('Contains Firmar (Alumno)?', 'Firmar (Alumno)' in content)
    print('Snippet:\n', '\n'.join(content.split('\n')[:60]))
else:
    print('No creditos in DB to test contrato rendering')
