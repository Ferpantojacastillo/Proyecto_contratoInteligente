from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from usuarios.models import Usuario
from actividades.models import Actividad
from .models import Credito, SolicitudCredito
from django.http import HttpResponseForbidden
from django.db.models import Q



@login_required
def crear_credito(request):
    usuarios = Usuario.objects.filter(es_alumno=True)
    actividades = Actividad.objects.all().order_by("nombre")

    if request.method == "POST":
        alumno_id = request.POST.get("alumno_id")
        actividad_id = request.POST.get("actividad_id")
        nombre_manual = request.POST.get("nombre")
        tipo = request.POST.get("tipo")
        semestre = request.POST.get("semestre")
        fecha_liberacion = request.POST.get("fecha_liberacion")

        alumno = Usuario.objects.get(id=alumno_id)
        numero = alumno.numero_control

        # Si se seleccionó actividad, usar su nombre (incluir convo si existe)
        if actividad_id:
            actividad = Actividad.objects.get(id=actividad_id)
            if getattr(actividad, 'convo', None):
                nombre_final = f"{actividad.nombre} {actividad.convo}"
            else:
                nombre_final = actividad.nombre
        else:
            nombre_final = nombre_manual

        Credito.objects.create(
            alumno=alumno,
            nombre=nombre_final,
            tipo=tipo,
            semestre=semestre,
            numero_control=numero,
            fecha_liberacion=fecha_liberacion,
        )

        return redirect("mis_creditos")

    return render(request, "creditos/crear_credito.html", {
        "usuarios": usuarios,
        "actividades": actividades,
    })
@login_required
def mis_creditos(request):
    user = request.user
    # Mostrar créditos asignados al usuario o créditos sin alumno pero con número de control igual al usuario
    qs = Q(alumno=user)
    if getattr(user, 'numero_control', None):
        qs = qs | (Q(alumno__isnull=True) & Q(numero_control=user.numero_control))
    creditos = Credito.objects.filter(qs).order_by('-id')
    return render(request, 'creditos/mis_creditos.html', {
        'creditos': creditos
    })


@login_required
def asignar_credito(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)

    # If confirm posted, perform assignment
    if request.method == 'POST' and request.POST.get('confirm'):
        alumno_id = request.POST.get('alumno_id')
        try:
            alumno = Usuario.objects.get(id=alumno_id)
        except Usuario.DoesNotExist:
            messages.error(request, 'Alumno no encontrado para la confirmación.')
            return redirect('asignar_credito', id_credito)

        credito.alumno = alumno
        credito.numero_control = alumno.numero_control
        credito.liberado = True
        credito.fecha_liberacion = timezone.now().date()
        credito.save()
        messages.success(request, f'Crédito asignado y liberado a {alumno.username} ({alumno.numero_control}).')
        return redirect('lista_creditos_admin')

    confirm_user = None
    numero_control = request.POST.get('numero_control') or request.GET.get('numero_control')
    nombre = request.POST.get('nombre')

    # If a numero_control was provided, try exact match
    if numero_control:
        try:
            confirm_user = Usuario.objects.get(numero_control=numero_control, es_alumno=True)
        except Usuario.DoesNotExist:
            confirm_user = None
            messages.info(request, f'No se encontró alumno con número de control {numero_control}.')

    # If no exact match but a nombre partial provided, attempt search
    if not confirm_user and nombre:
        qs = Usuario.objects.filter(username__icontains=nombre, es_alumno=True)
        if qs.count() == 1:
            confirm_user = qs.first()
        elif qs.count() > 1:
            # take first but notify
            confirm_user = qs.first()
            messages.info(request, 'Se encontraron varias coincidencias; usando la primera.')

    return render(request, 'creditos/asignar_credito.html', {
        'credito': credito,
        'confirm_user': confirm_user,
        'numero_control': numero_control,
        'nombre': nombre,
    })


@login_required
def panel_creditos(request):
    creditos = Credito.objects.all().order_by('-id')
    return render(request, 'creditos/panel_creditos.html', {'creditos': creditos})


@login_required
def lista_creditos_admin(request):
    creditos = Credito.objects.all().order_by('-id')
    return render(request, 'creditos/lista_creditos_admin.html', {'creditos': creditos})


@login_required
def solicitar_credito(request):
    if request.method == 'POST':
        # Minimal handling: create a SolicitudCredito if posted
        alumno = request.user
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        semestre = request.POST.get('semestre')
        numero_control = request.POST.get('numero_control', alumno.numero_control if hasattr(alumno, 'numero_control') else '')
        SolicitudCredito.objects.create(alumno=alumno, nombre=nombre, tipo=tipo, semestre=semestre, numero_control=numero_control)
        messages.success(request, 'Solicitud enviada.')
        return redirect('mis_creditos')
    return render(request, 'creditos/solicitar_credito.html')


@login_required
def lista_solicitudes(request):
    solicitudes = SolicitudCredito.objects.all().order_by('-creado_en')
    return render(request, 'creditos/lista_solicitudes.html', {'solicitudes': solicitudes})


@login_required
def aprobar_solicitud(request, id_solicitud):
    s = get_object_or_404(SolicitudCredito, id=id_solicitud)
    s.estado = 'aprobado'
    s.revisado_por = request.user
    s.revisado_en = timezone.now()
    s.save()
    messages.success(request, 'Solicitud aprobada.')
    return redirect('lista_solicitudes')


@login_required
def rechazar_solicitud(request, id_solicitud):
    s = get_object_or_404(SolicitudCredito, id=id_solicitud)
    s.estado = 'rechazado'
    s.revisado_por = request.user
    s.revisado_en = timezone.now()
    s.save()
    messages.success(request, 'Solicitud rechazada.')
    return redirect('lista_solicitudes')


@login_required
def contrato(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    return render(request, 'creditos/contrato.html', {'credito': credito})


@login_required
def liberar_credito(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')
    credito.liberado = True
    credito.fecha_liberacion = timezone.now().date()
    credito.save()
    messages.success(request, 'Crédito liberado.')
    return redirect('lista_creditos_admin')


@login_required
def eliminar_credito(request, id_credito):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')
    credito = get_object_or_404(Credito, id=id_credito)
    credito.delete()
    messages.success(request, 'Crédito eliminado.')
    return redirect('lista_creditos_admin')


@login_required
def lista_creditos_docente(request):
    creditos = Credito.objects.all().order_by('-id')
    return render(request, 'creditos/lista_creditos_docente.html', {'creditos': creditos})


@login_required
def docente_asignar(request):
    """Lista de créditos para que el docente pueda asignar (liberar) a alumnos.
    Solo accesible para usuarios con `es_docente=True`.
    """
    if not request.user.es_docente:
        return HttpResponseForbidden('Permisos insuficientes')

    creditos = Credito.objects.filter(liberado=False).order_by('-id')
    return render(request, 'creditos/lista_creditos_docente_asignar.html', {'creditos': creditos})


@login_required
def docente_liberar_credito(request, id_credito):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')

    if not getattr(request.user, 'es_docente', False):
        return HttpResponseForbidden('Permisos insuficientes')

    credito = get_object_or_404(Credito, id=id_credito)
    credito.liberado = True
    credito.fecha_liberacion = timezone.now().date()
    credito.save()
    messages.success(request, 'Crédito liberado por docente.')
    return redirect('docente_asignar')


@login_required
def firmar_por_docente(request, id_credito):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')
    
    credito = get_object_or_404(Credito, id=id_credito)
    # El docente solo puede firmar si el crédito fue asignado por el admin (liberado)
    if not credito.liberado:
        messages.error(request, 'El crédito no ha sido liberado por el administrador aún.')
        return redirect('docente_dashboard')
    
    credito.firmado_docente = True
    credito.firmado_docente_por = request.user
    credito.firmado_docente_en = timezone.now()
    credito.save()
    messages.success(request, 'Crédito firmado por docente.')
    return redirect('docente_dashboard')


@login_required
def firmar_por_alumno(request, id_credito):
    # Sólo aceptar POST para firmar
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')

    credito = get_object_or_404(Credito, id=id_credito)

    # Verificar que el usuario es el alumno asignado o que el número de control coincide
    usuario = request.user
    numero_ok = credito.numero_control and usuario.numero_control and credito.numero_control.strip() == usuario.numero_control.strip()
    if not (credito.alumno == usuario or numero_ok):
        messages.error(request, 'No tienes permiso para firmar este crédito.')
        return redirect('mis_creditos')

    # Si el crédito no tiene alumno asignado, asignarlo al firmante
    if credito.alumno is None:
        credito.alumno = usuario

    credito.firmado_alumno = True
    credito.firmado_alumno_por = usuario
    credito.firmado_alumno_en = timezone.now()
    credito.save()
    messages.success(request, 'Crédito firmado por alumno.')
    return redirect('mis_creditos')


@login_required
def firmar_por_admin(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    credito.firmado_admin = True
    credito.firmado_admin_por = request.user
    credito.firmado_admin_en = timezone.now()
    credito.save()
    messages.success(request, 'Crédito firmado por admin.')
    return redirect('lista_creditos_admin')


from usuarios.views import login_view as usuarios_login_view


def docente_login(request):
    # Delegate to the usuarios app login_view so behaviour and templates stay consistent
    return usuarios_login_view(request)


@login_required
def docente_dashboard(request):
    # Obtener todas las actividades
    actividades = Actividad.objects.all().order_by('nombre')
    
    # Obtener créditos pendientes de firma por el docente:
    # - El crédito debe estar liberado (asignado por admin)
    # - Aún no ha sido firmado por el docente (firmado_docente = False)
    creditos_por_firmar = Credito.objects.filter(
        liberado=True,
        firmado_docente=False
    ).order_by('-id')
    
    return render(request, 'creditos/docente_dashboard.html', {
        'actividades': actividades,
        'creditos': creditos_por_firmar,
    })


@login_required
def wallet(request):
    return render(request, 'creditos/wallet.html')


@login_required
def credito_pdf(request, id_credito):
    """Genera un PDF para un crédito completamente firmado (por alumno Y docente).

    El PDF solo se genera si AMBOS (alumno y docente) han firmado el crédito.
    """
    import io
    import os
    from pathlib import Path
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except Exception:
        return render(request, 'creditos/pdf_error.html', {
            'error': 'La librería reportlab no está instalada. Ejecuta: pip install reportlab'
        }, status=500)

    credito = get_object_or_404(Credito, id=id_credito)

    # Solo el alumno propietario puede generar su PDF
    if credito.alumno != request.user:
        messages.error(request, 'No tienes permiso para generar este documento.')
        return redirect('mis_creditos')
    
    # El PDF solo se genera si AMBOS firman (alumno Y docente)
    if not (credito.firmado_alumno and credito.firmado_docente):
        messages.error(request, 'El crédito debe estar firmado por ti (alumno) y por el docente para descargar el PDF.')
        return redirect('mis_creditos')

    # Crear carpeta documentos si no existe (en la raíz del proyecto, al lado de manage.py)
    from django.conf import settings
    docs_dir = Path(settings.BASE_DIR) / 'documentos'
    docs_dir.mkdir(exist_ok=True)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Encabezado simple
    p.setFont('Helvetica-Bold', 16)
    p.drawString(72, 800, 'Constancia de Crédito')

    # Datos del alumno
    nombre = request.user.get_full_name() or request.user.username
    numero_control = request.user.numero_control or request.user.username

    p.setFont('Helvetica', 12)
    p.drawString(72, 760, f'Nombre: {nombre}')
    p.drawString(72, 740, f'Número de control: {numero_control}')

    # Información del crédito
    p.drawString(72, 710, f'Crédito: {credito.nombre}')
    p.drawString(72, 690, f'Tipo: {credito.get_tipo_display()}')
    p.drawString(72, 670, f'Semestre: {credito.semestre}')
    p.drawString(72, 650, f'Fecha de liberación: {credito.fecha_liberacion or "--"}')

    p.showPage()
    p.save()

    buffer.seek(0)
    # Nombre único por crédito: número de control + id del crédito
    safe_num = (str(numero_control).replace(' ', '_'))
    filename = f"{safe_num}-credito-{credito.id}.pdf"
    filepath = docs_dir / filename

    # Guardar PDF en archivo del proyecto
    try:
        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())
    except Exception as e:
        messages.error(request, f'Error al guardar PDF en el proyecto: {e}')
        return redirect('mis_creditos')

    # También guardar una copia en la carpeta 'Documents' del usuario del sistema (si existe)
    try:
        user_docs = Path.home() / 'Documents'
        user_docs.mkdir(parents=True, exist_ok=True)
        user_filepath = user_docs / filename
        with open(user_filepath, 'wb') as f2:
            f2.write(buffer.getvalue())
    except Exception:
        # No bloquear si no se pudo escribir en Documents; sólo informamos con mensaje opcional
        user_filepath = None

    # Devolver el PDF como respuesta de descarga
    try:
        from django.http import HttpResponse
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        if user_filepath:
            messages.success(request, f'PDF guardado en: {user_filepath}')
        else:
            messages.success(request, f'PDF generado: {filename}')
        return response
    except Exception as e:
        messages.error(request, f'Error al preparar la descarga: {e}')
        return redirect('mis_creditos')

