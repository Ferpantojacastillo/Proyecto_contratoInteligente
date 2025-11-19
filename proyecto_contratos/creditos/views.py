from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Credito
from usuarios.models import Usuario
from datetime import date
from django.contrib import messages
from django.utils import timezone
from .models import SolicitudCredito
from usuarios.models import Usuario as UsuarioModel
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth import login as auth_login

@login_required
def mis_creditos(request):
    creditos = Credito.objects.filter(alumno=request.user)
    return render(request, 'creditos/mis_creditos.html', {'creditos': creditos})

@login_required
def wallet(request):
    if request.user.rol != 'admin':
        return redirect('inicio')
    return render(request, 'creditos/wallet.html', {'wallet': request.user.wallet})

@login_required
def liberar_credito(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if is_admin:
        credito.liberado = True
        credito.fecha_liberacion = date.today()
        credito.firmado_admin = True
        credito.firmado_admin_por = request.user
        credito.firmado_admin_en = timezone.now()
        if not credito.alumno and credito.numero_control:
            try:
                posible = UsuarioModel.objects.filter(numero_control=credito.numero_control).first()
                if posible:
                    credito.alumno = posible
            except Exception:
                nombre = credito.nombre or ''
                posible_qs = UsuarioModel.objects.filter(username__icontains=nombre)
                if posible_qs.exists():
                    credito.alumno = posible_qs.first()
        credito.save()
    return redirect('inicio')
@login_required
def panel_creditos(request):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        return redirect('/inicio/')
    creditos = Credito.objects.order_by('-id')
    return render(request, 'creditos/panel_creditos.html', {'creditos': creditos})


@login_required
def lista_creditos_admin(request):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, 'No tienes permiso para ver esta página.')
        return redirect('inicio')

    creditos = Credito.objects.order_by('-id')
    return render(request, 'creditos/lista_creditos_admin.html', {'creditos': creditos})


@login_required
def asignar_credito(request, id_credito):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('inicio')

    credito = get_object_or_404(Credito, id=id_credito)

    if request.method == 'POST':
        # Two-step flow: first POST finds/identifies the user and asks for confirmation.
        # Second POST includes 'confirm' to perform the assignment.
        confirm = request.POST.get('confirm')
        numero_control = request.POST.get('numero_control', '').strip()
        nombre = request.POST.get('nombre', '').strip()

        # If this is the confirmation POST, perform the assignment using alumno_id
        if confirm == '1':
            alumno_id = request.POST.get('alumno_id')
            usuario_encontrado = None
            if alumno_id:
                try:
                    usuario_encontrado = UsuarioModel.objects.get(id=alumno_id)
                except UsuarioModel.DoesNotExist:
                    usuario_encontrado = None

            if not usuario_encontrado:
                messages.error(request, 'Usuario no válido para asignación. Intenta de nuevo.')
                return render(request, 'creditos/asignar_credito.html', {'credito': credito})

            credito.alumno = usuario_encontrado
            credito.liberado = True
            credito.fecha_liberacion = date.today()
            credito.firmado_admin = True
            credito.firmado_admin_por = request.user
            credito.firmado_admin_en = timezone.now()
            if numero_control:
                credito.numero_control = numero_control
            credito.save()

            messages.success(request, f'Crédito asignado y liberado a {usuario_encontrado.username}.')
            return redirect('lista_creditos_admin')

        # Initial POST: locate user and show confirmation
        usuario_encontrado = None
        if numero_control:
            usuario_encontrado = UsuarioModel.objects.filter(numero_control=numero_control).first()
            if not usuario_encontrado:
                messages.error(request, 'No se encontró un alumno con ese número de control. Verifica el número y vuelve a intentar.')
                return render(request, 'creditos/asignar_credito.html', {'credito': credito, 'numero_control': numero_control, 'nombre': nombre})
            # render confirmation
            return render(request, 'creditos/asignar_credito.html', {'credito': credito, 'confirm_user': usuario_encontrado, 'numero_control': numero_control})

        # If no numero_control, search by nombre
        if nombre:
            qs = UsuarioModel.objects.filter(username__icontains=nombre)
            if not qs.exists():
                messages.error(request, 'No se encontró ningún alumno con ese nombre.')
                return render(request, 'creditos/asignar_credito.html', {'credito': credito, 'nombre': nombre})
            if qs.count() > 1:
                messages.error(request, 'Hay múltiples usuarios con ese nombre parcial. Usa el número de control para asignar con seguridad.')
                return render(request, 'creditos/asignar_credito.html', {'credito': credito, 'nombre': nombre})
            usuario_encontrado = qs.first()
            return render(request, 'creditos/asignar_credito.html', {'credito': credito, 'confirm_user': usuario_encontrado})

        messages.error(request, 'Debes introducir el número de control del alumno o su nombre para buscarlo.')
        return render(request, 'creditos/asignar_credito.html', {'credito': credito})

    return render(request, 'creditos/asignar_credito.html', {'credito': credito})

@login_required
def crear_credito(request):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, 'No tienes permiso para crear créditos. Contacta al administrador.')
        return redirect('mis_creditos')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        semestre = request.POST.get('semestre')
        fecha_liberacion = request.POST.get('fecha_liberacion')
        numero_control = request.POST.get('numero_control')
        alumno_id = request.POST.get('alumno_id')

        alumno = None
        if alumno_id:
            try:
                alumno = Usuario.objects.get(id=alumno_id)
            except Usuario.DoesNotExist:
                alumno = None

        if not alumno:
            messages.error(request, 'Alumno no válido.')
            return redirect('crear_credito')

        actual_count = Credito.objects.filter(alumno=alumno).count()
        if actual_count >= 5:
            messages.error(request, 'El alumno ya tiene 5 créditos registrados.')
            return redirect('crear_credito')

        credito = Credito(
            alumno=alumno,
            nombre=nombre,
            tipo=tipo,
            semestre=semestre,
            numero_control=numero_control or ''
        )

        if fecha_liberacion:
            try:
                credito.fecha_liberacion = fecha_liberacion
                credito.liberado = True
                credito.firmado_admin = True
                credito.firmado_admin_por = request.user
                credito.firmado_admin_en = timezone.now()
            except Exception:
                pass

        credito.save()
        messages.success(request, 'Crédito creado correctamente.')
        return redirect('panel_creditos')

    context = {'usuarios': Usuario.objects.filter(is_active=True)}
    return render(request, 'creditos/crear_credito.html', context)


@login_required
def firmar_por_alumno(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    if credito.alumno != request.user:
        messages.error(request, "No puedes firmar este crédito.")
        return redirect('mis_creditos')
    if not credito.liberado:
        messages.error(request, "El crédito no está liberado todavía.")
        return redirect('mis_creditos')
    credito.firmado_alumno = True
    credito.firmado_alumno_por = request.user
    credito.firmado_alumno_en = timezone.now()
    credito.save()
    messages.success(request, "Has firmado el crédito correctamente.")
    return redirect('mis_creditos')


@login_required
def firmar_por_admin(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, "No tienes permiso para firmar como admin.")
        return redirect('mis_creditos')
    if not credito.liberado:
        messages.error(request, "El crédito no está liberado todavía.")
        return redirect('mis_creditos')
    credito.firmado_admin = True
    credito.fecha_liberacion = date.today()
    credito.firmado_admin_por = request.user
    credito.firmado_admin_en = timezone.now()
    if not credito.alumno and credito.numero_control:
        try:
            posible = UsuarioModel.objects.filter(numero_control=credito.numero_control).first()
            if posible:
                credito.alumno = posible
        except Exception:
            pass
    credito.save()
    messages.success(request, "Has firmado el crédito como administrador.")
    return redirect('mis_creditos')


@login_required
def contrato(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    return render(request, 'creditos/contrato.html', {'credito': credito})


@login_required
def lista_creditos_docente(request):
    # Solo docentes pueden acceder
    if not getattr(request.user, 'es_docente', False):
        messages.error(request, 'No tienes permiso para acceder a la zona de docente.')
        return redirect('inicio')

    # Mostrar créditos tipo 'academico' que estén liberados y no firmados por docente
    creditos = Credito.objects.filter(tipo='academico', liberado=True, firmado_docente=False).order_by('-id')
    return render(request, 'creditos/lista_creditos_docente.html', {'creditos': creditos})


def docente_login(request):
    # Login para docentes: username o numero_control + contraseña docente asignada por admin
    if request.method == 'POST':
        identificador = request.POST.get('identificador', '').strip()
        password = request.POST.get('password', '').strip()

        usuario = None
        if identificador:
            # buscar por username exacto (case-insensitive)
            usuario = UsuarioModel.objects.filter(username__iexact=identificador, es_docente=True).first()
            if not usuario:
                # buscar por numero_control
                usuario = UsuarioModel.objects.filter(numero_control=identificador, es_docente=True).first()

        if not usuario:
            messages.error(request, 'No existe un docente con ese usuario o número de control.')
            return render(request, 'usuarios/docente_login.html')

        if not usuario.check_docente_password(password):
            messages.error(request, 'Contraseña docente incorrecta.')
            return render(request, 'usuarios/docente_login.html')

        # login y redirigir al dashboard docente
        auth_login(request, usuario)
        return redirect('docente_dashboard')

    return render(request, 'usuarios/docente_login.html')


@login_required
def docente_dashboard(request):
    if not getattr(request.user, 'es_docente', False):
        messages.error(request, 'No tienes permiso para acceder a la zona de docente.')
        return redirect('inicio')

    # Créditos pendientes de firma por docente
    creditos_pendientes = Credito.objects.filter(tipo='academico', liberado=True, firmado_docente=False).order_by('-id')

    # Manejar creación rápida de crédito por docente (registro de alumno + crédito)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        numero_control = request.POST.get('numero_control', '').strip()
        tipo = request.POST.get('tipo', 'academico').strip()
        semestre = request.POST.get('semestre', '').strip()

        if not nombre or not numero_control:
            messages.error(request, 'Nombre y número de control son requeridos para registrar un alumno.')
            return redirect('docente_dashboard')

        alumno = UsuarioModel.objects.filter(numero_control=numero_control).first()
        if not alumno:
            # crear un usuario básico para el alumno; no podrá iniciar sesión hasta que el admin le asigne contraseña
            alumno = UsuarioModel.objects.create(username=nombre, numero_control=numero_control, es_alumno=True)
            alumno.set_unusable_password()
            alumno.save()

        # evitar más de 5 créditos
        if Credito.objects.filter(alumno=alumno).count() >= 5:
            messages.error(request, 'El alumno ya tiene 5 créditos registrados.')
            return redirect('docente_dashboard')

        credito = Credito.objects.create(
            alumno=alumno,
            nombre=nombre,
            tipo=tipo,
            semestre=semestre,
            numero_control=numero_control
        )
        messages.success(request, f'Crédito creado para {alumno.username}. El administrador liberará cuando corresponda.')
        return redirect('docente_dashboard')

    return render(request, 'creditos/docente_dashboard.html', {'creditos': creditos_pendientes})


@login_required
@require_POST
def firmar_por_docente(request, id_credito):
    # Solo docentes pueden firmar
    if not getattr(request.user, 'es_docente', False):
        messages.error(request, 'No tienes permiso para firmar créditos como docente.')
        return redirect('inicio')

    credito = get_object_or_404(Credito, id=id_credito)
    if credito.tipo != 'academico':
        messages.error(request, 'Solo se pueden firmar créditos académicos en esta sección.')
        return redirect('lista_creditos_docente')

    if not credito.liberado:
        messages.error(request, 'El crédito todavía no está liberado.')
        return redirect('lista_creditos_docente')

    credito.firmado_docente = True
    credito.firmado_docente_por = request.user
    credito.firmado_docente_en = timezone.now()
    credito.save()
    messages.success(request, f'Has firmado el crédito académico "{credito.nombre}" para {credito.alumno.username if credito.alumno else "(sin alumno)"}.')
    return redirect('lista_creditos_docente')


@login_required
def solicitar_credito(request):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if is_admin:
        messages.error(request, 'Los administradores no pueden solicitar créditos.')
        return redirect('panel_creditos')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        semestre = request.POST.get('semestre')
        numero_control = request.POST.get('numero_control')

        SolicitudCredito.objects.create(
            alumno=request.user,
            nombre=nombre,
            tipo=tipo,
            semestre=semestre,
            numero_control=numero_control or ''
        )
        messages.success(request, 'Solicitud enviada. El administrador la revisará.')
        return redirect('mis_creditos')

    return render(request, 'creditos/solicitar_credito.html')


@login_required
def lista_solicitudes(request):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, 'No tienes permiso para ver las solicitudes.')
        return redirect('inicio')

    solicitudes = SolicitudCredito.objects.order_by('-creado_en')
    return render(request, 'creditos/lista_solicitudes.html', {'solicitudes': solicitudes})


@login_required
def aprobar_solicitud(request, id_solicitud):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, 'No tienes permiso.')
        return redirect('inicio')

    solicitud = get_object_or_404(SolicitudCredito, id=id_solicitud)
    if solicitud.estado != 'pendiente':
        messages.error(request, 'Solicitud ya revisada.')
        return redirect('lista_solicitudes')

    credito = Credito.objects.create(
        alumno=solicitud.alumno,
        nombre=solicitud.nombre,
        tipo=solicitud.tipo,
        semestre=solicitud.semestre,
        numero_control=solicitud.numero_control,
        fecha_liberacion=None,
        liberado=False
    )
    if solicitud.numero_control:
        try:
            u = UsuarioModel.objects.filter(numero_control=solicitud.numero_control).first()
            if u:
                credito.alumno = u
                credito.save()
        except Exception:
            pass
    solicitud.estado = 'aprobado'
    solicitud.revisado_por = request.user
    solicitud.revisado_en = timezone.now()
    solicitud.save()

    messages.success(request, f'Solicitud {solicitud.id} aprobada y crédito creado.')
    return redirect('lista_solicitudes')


@login_required
def rechazar_solicitud(request, id_solicitud):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, 'No tienes permiso.')
        return redirect('inicio')

    solicitud = get_object_or_404(SolicitudCredito, id=id_solicitud)
    if solicitud.estado != 'pendiente':
        messages.error(request, 'Solicitud ya revisada.')
        return redirect('lista_solicitudes')

    solicitud.estado = 'rechazado'
    solicitud.revisado_por = request.user
    solicitud.revisado_en = timezone.now()
    solicitud.save()
    messages.success(request, f'Solicitud {solicitud.id} rechazada.')
    return redirect('lista_solicitudes')


@login_required
def eliminar_credito(request, id_credito):
    is_admin = getattr(request.user, 'es_admin_creditos', False) or request.user.is_staff
    if not is_admin:
        messages.error(request, 'No tienes permiso para eliminar créditos.')
        return redirect('lista_creditos_admin')

    credito = get_object_or_404(Credito, id=id_credito)

    if request.method == 'POST':
        nombre = credito.nombre or ''
        credito.delete()
        messages.success(request, f"Crédito '{nombre}' eliminado correctamente.")
        return redirect('lista_creditos_admin')

    return redirect('lista_creditos_admin')


 
