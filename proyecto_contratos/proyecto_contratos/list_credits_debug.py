#!/usr/bin/env python
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from creditos.models import Credito
from usuarios.models import Usuario

print('Usuarios docentes activos:')
for u in Usuario.objects.filter(es_docente=True):
    print('- ', u.username, 'active=', u.is_active)

print('\nÚltimos 50 créditos:')
for c in Credito.objects.all().order_by('-id')[:50]:
    print(f'id={c.id} nombre="{c.nombre}" liberado={c.liberado} firmado_alumno={c.firmado_alumno} firmado_docente={c.firmado_docente} alumno={getattr(c.alumno, "username", None)} numero_control={c.numero_control}')
