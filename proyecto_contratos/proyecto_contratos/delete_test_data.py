#!/usr/bin/env python
"""
Elimina usuarios y créditos de prueba creados durante las pruebas.
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from creditos.models import Credito
from actividades.models import Actividad

User = get_user_model()

# Definir patrones/usuarios a eliminar
usernames_to_delete = ['portal_check_doc', 'portal_alum_1']
credit_name_prefixes = ['PORTALCHECK_', 'PORTALALUM_']

# Borrar créditos por prefijo de nombre
deleted_credits = 0
for p in credit_name_prefixes:
    qs = Credito.objects.filter(nombre__startswith=p)
    n = qs.count()
    if n:
        qs.delete()
        deleted_credits += n

# Borrar usuarios específicos
deleted_users = 0
for u in usernames_to_delete:
    obj = User.objects.filter(username=u)
    n = obj.count()
    if n:
        obj.delete()
        deleted_users += n

# También intentar limpiar créditos no asignados antiguos que fueron creados con estos nombres exactos
extra_qs = Credito.objects.filter(nombre='PORTALALUM_CREDIT')
if extra_qs.exists():
    deleted_credits += extra_qs.count()
    extra_qs.delete()

print(f"Usuarios eliminados: {deleted_users}")
print(f"Créditos eliminados: {deleted_credits}")

# Listar si queda alguno (comprobación)
print('Créditos restantes con prefijos de prueba:')
for p in credit_name_prefixes:
    for c in Credito.objects.filter(nombre__startswith=p):
        print('-', c.id, c.nombre)

print('Usuarios restantes con nombres de prueba:')
for u in User.objects.filter(username__in=usernames_to_delete):
    print('-', u.username)
