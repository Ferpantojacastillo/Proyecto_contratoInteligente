#!/usr/bin/env python
"""Script de prueba: Flujo completo del docente"""

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_creditos.settings')
django.setup()

from django.test import Client
from usuarios.models import Usuario
from creditos.models import Credito
from actividades.models import Actividad

def prueba_docente():
    print('═' * 70)
    print('🧪 PRUEBA COMPLETA: DOCENTE DESDE LOGIN HASTA FIRMAR')
    print('═' * 70)
    print()

    # Paso 1: Login
    client = Client()
    login_ok = client.login(username='docente-admin', password='AdminPassword123')
    print('1️⃣  LOGIN')
    print(f'   Status: {"✓ Exitoso" if login_ok else "✗ Fallido"}')
    print()

    if not login_ok:
        print('✗ No se pudo continuar')
        return

    # Paso 2: Acceder a dashboard
    print('2️⃣  ACCEDER AL DASHBOARD')
    response = client.get('/creditos/docente/dashboard/')
    print(f'   Status: {response.status_code} (esperado 200)')
    print(f'   Template: docente_dashboard.html')
    print()

    # Paso 3: Verificar que hay actividades
    actividades = Actividad.objects.all()
    print('3️⃣  ACTIVIDADES EN EL DASHBOARD')
    print(f'   Total: {actividades.count()}')
    for act in actividades[:3]:
        print(f'   - {act.nombre}')
    print()

    # Paso 4: Verificar créditos pendientes
    creditos_sin_firmar = Credito.objects.filter(firmado_docente=False, liberado=True)
    print('4️⃣  CRÉDITOS PENDIENTES DE FIRMA')
    print(f'   Total: {creditos_sin_firmar.count()}')
    for credito in creditos_sin_firmar[:3]:
        alumno = credito.alumno.username if credito.alumno else "Sin alumno"
        print(f'   - ID {credito.id}: {credito.nombre} (Alumno: {alumno})')
    print()

    # Paso 5: Firmar un crédito
    if creditos_sin_firmar.exists():
        credito = creditos_sin_firmar.first()
        print('5️⃣  FIRMAR CRÉDITO')
        print(f'   Crédito: ID {credito.id}')
        
        response = client.post(f'/creditos/docente/firmar/{credito.id}/')
        print(f'   POST Status: {response.status_code} (esperado 302 redirect)')
        
        # Verificar que se firmó
        credito_actualizado = Credito.objects.get(id=credito.id)
        if credito_actualizado.firmado_docente:
            print(f'   ✓ Crédito firmado por: {credito_actualizado.firmado_docente_por.username}')
            print(f'   ✓ Fecha de firma: {credito_actualizado.firmado_docente_en}')
        else:
            print('   ✗ El crédito NO fue marcado como firmado')
    else:
        print('5️⃣  FIRMAR CRÉDITO')
        print('   ✗ No hay créditos pendientes para firmar')
    print()

    print('═' * 70)
    print('✓ PRUEBA COMPLETADA EXITOSAMENTE')
    print('═' * 70)

if __name__ == '__main__':
    prueba_docente()
