from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from usuarios.models import Usuario
from actividades.models import Actividad
from .models import Credito, SolicitudCredito
from django.http import HttpResponseForbidden



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
    creditos = Credito.objects.filter(alumno=request.user).order_by('-id')
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
def firmar_por_docente(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    credito.firmado_docente = True
    credito.firmado_docente_por = request.user
    credito.firmado_docente_en = timezone.now()
    credito.save()
    messages.success(request, 'Crédito firmado por docente.')
    return redirect('lista_creditos_docente')


@login_required
def firmar_por_alumno(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    credito.firmado_alumno = True
    credito.firmado_alumno_por = request.user
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
    return render(request, 'creditos/docente_dashboard.html')


@login_required
def wallet(request):
    return render(request, 'creditos/wallet.html')


@login_required
def credito_pdf(request, id_credito):
    """Genera un PDF sencillo para un crédito terminado (liberado).

    El PDF incluirá el número de control y el nombre del alumno. El archivo
    resultante tendrá como nombre `<numero_control>.pdf`.
    """
    import io
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
    except Exception:
        return render(request, 'creditos/pdf_error.html', {
            'error': 'La librería reportlab no está instalada. Ejecuta: pip install reportlab'
        }, status=500)

    credito = get_object_or_404(Credito, id=id_credito)

    # Solo el alumno propietario puede descargar su PDF (y debe estar liberado)
    if not credito.liberado:
        return HttpResponseForbidden('El crédito no está liberado todavía.')
    if credito.alumno != request.user:
        return HttpResponseForbidden('No tienes permiso para descargar este documento.')

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
    filename = f"{numero_control}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

