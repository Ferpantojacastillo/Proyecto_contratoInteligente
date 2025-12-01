from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Actividad
from .forms import ActividadForm
from creditos.models import Credito
from usuarios.models import Usuario
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden


def es_admin(user):
    return user.is_authenticated and (user.is_staff or getattr(user, 'es_admin_creditos', False))


@login_required
def lista_actividades(request):
    actividades = Actividad.objects.order_by('fecha')
    return render(request, 'actividades/lista_actividades.html', {'actividades': actividades})


@login_required
def detalle_actividad(request, id_actividad):
    actividad = get_object_or_404(Actividad, id=id_actividad)
    esta_inscrito = request.user in actividad.inscritos.all()
    # Buscar si existe un crédito vinculado para el usuario actual y esta actividad
    credito_usuario = None
    if request.user.is_authenticated:
        try:
            num = getattr(request.user, 'numero_control', None)
            credito_qs = Credito.objects.filter(
                Q(alumno=request.user) |
                (Q(alumno__isnull=True) & Q(numero_control=num))
            ).filter(nombre__icontains=actividad.nombre)
            credito_usuario = credito_qs.order_by('-id').first()
        except Exception:
            credito_usuario = None
    return render(request, 'actividades/detalle.html', {
        'actividad': actividad,
        'esta_inscrito': esta_inscrito
        , 'credito_usuario': credito_usuario
    })


@login_required
def firmar_actividad_credito(request, id_actividad):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')

    actividad = get_object_or_404(Actividad, id=id_actividad)

    # Sólo alumnos pueden firmar
    if request.user.is_staff or getattr(request.user, 'es_admin_creditos', False):
        messages.error(request, 'Solo alumnos pueden firmar este crédito.')
        return redirect('detalle_actividad', id_actividad=id_actividad)

    usuario = request.user

    # Buscar crédito existente del alumno o por numero_control/actividad
    num = getattr(usuario, 'numero_control', None)
    credito = Credito.objects.filter(Q(alumno=usuario) | (Q(alumno__isnull=True) & Q(numero_control=num))).filter(nombre__icontains=actividad.nombre).order_by('-id').first()

    if not credito:
        credito = Credito.objects.create(
            alumno=usuario,
            nombre=f"{actividad.nombre} {actividad.convo}" if getattr(actividad, 'convo', '') else actividad.nombre,
            tipo=actividad.tipo,
            semestre='--',
            numero_control=num or '',
            liberado=False,
        )

    # Asignar alumno si faltaba y marcar firmado por alumno
    if credito.alumno is None:
        credito.alumno = usuario

    credito.firmado_alumno = True
    credito.firmado_alumno_por = usuario
    credito.firmado_alumno_en = timezone.now()
    credito.save()
    messages.success(request, 'Has firmado el crédito para esta actividad.')
    return redirect('mis_creditos')


@login_required
def inscribirse(request, id_actividad):
    actividad = get_object_or_404(Actividad, id=id_actividad)

    if actividad.capacidad and actividad.inscritos.count() >= actividad.capacidad:
        messages.error(request, "Capacidad llena.")
        return redirect('detalle_actividad', id_actividad=id_actividad)

    actividad.inscritos.add(request.user)

    # Crear un crédito asociado a la inscripción si no existe
    from creditos.models import Credito
    usuario = request.user
    exists = Credito.objects.filter(alumno=usuario, nombre=actividad.nombre, tipo=actividad.tipo).exists()
    if not exists:
        Credito.objects.create(
            alumno=usuario,
            nombre=f"{actividad.nombre} {actividad.convo}" if getattr(actividad, 'convo', '') else actividad.nombre,
            tipo=actividad.tipo,
            semestre='--',
            numero_control=getattr(usuario, 'numero_control', '') or '',
            liberado=False,
        )

    messages.success(request, "Te inscribiste correctamente. Se creó tu solicitud de crédito (pendiente de liberación).")
    return redirect('detalle_actividad', id_actividad=id_actividad)


@login_required
def registrar_actividad(request):
    if not es_admin(request.user):
        messages.error(request, "No tienes permiso para registrar actividades.")
        return redirect('lista_actividades')

    if request.method == 'POST':
        form = ActividadForm(request.POST)
        if form.is_valid():
            actividad = form.save(commit=False)

            encargado_manual = form.cleaned_data.get('encargado_manual', '').strip()
            if encargado_manual:
                
                posible = Usuario.objects.filter(username__iexact=encargado_manual).first()
                if not posible:
                    posible = Usuario.objects.filter(username__icontains=encargado_manual).first()

                if posible:
                    actividad.encargado = posible
                else:
                    
                    try:
                        nuevo = Usuario(username=encargado_manual, es_alumno=False)
                        nuevo.set_unusable_password()
                        nuevo.save()
                        actividad.encargado = nuevo
                        messages.info(request, f"Se creó el usuario '{encargado_manual}' como encargado.")
                    except Exception as e:
                        messages.error(request, f"No se pudo crear el usuario encargado: {e}")

            actividad.creado_por = request.user
            actividad.save()
            messages.success(request, "Actividad registrada correctamente.")
            return redirect('panel_actividades')
        else:
            messages.error(request, "Error al registrar la actividad. Verifica los datos.")
    else:
        form = ActividadForm()

    return render(request, 'actividades/registrar_actividades.html', {'form': form})


@login_required
def panel_actividades(request):
    if not es_admin(request.user):
        return redirect('lista_actividades')

    actividades = Actividad.objects.all().order_by('-fecha')
    return render(request, 'actividades/panel_admin.html', {'actividades': actividades})


@login_required
def registrar_credito(request, id_actividad, id_usuario):
    if not es_admin(request.user):
        return redirect('lista_actividades')

    actividad = get_object_or_404(Actividad, id=id_actividad)
    user = get_object_or_404(Usuario, id=id_usuario)

    
    Credito.objects.create(
        alumno=user,
        nombre=actividad.nombre,
        tipo=actividad.tipo,
    semestre='--',
        fecha_liberacion=None,
        liberado=True,
        firmado_admin=True,
        firmado_alumno=False
    )

    messages.success(request, f"Crédito registrado para {user.username}.")
    return redirect('panel_actividades')


 
@login_required
def liberar_actividad(request, id_actividad):
    actividad = get_object_or_404(Actividad, id=id_actividad)

    
    if not (es_admin(request.user) or request.user == actividad.creado_por or request.user == actividad.encargado):
        messages.error(request, "No tienes permiso para cambiar el estado de liberación.")
        return redirect('panel_actividades')

    
    actividad.liberado = not actividad.liberado
    if actividad.liberado:
        actividad.liberado_por = request.user
        actividad.fecha_liberacion = timezone.now()
        messages.success(request, f"Actividad '{actividad.nombre}' marcada como liberada.")
    else:
        actividad.liberado_por = None
        actividad.fecha_liberacion = None
        messages.success(request, f"Actividad '{actividad.nombre}' marcada como pendiente.")

    actividad.save()
    return redirect(request.META.get('HTTP_REFERER', 'panel_actividades'))


@login_required
def eliminar_actividad(request, id_actividad):
    actividad = get_object_or_404(Actividad, id=id_actividad)

    
    if not (es_admin(request.user) or request.user == actividad.creado_por or request.user == actividad.encargado):
        messages.error(request, "No tienes permiso para eliminar esta actividad.")
        return redirect('panel_actividades')

    if request.method == 'POST':
        nombre = actividad.nombre
        actividad.delete()
        messages.success(request, f"Actividad '{nombre}' eliminada correctamente.")
        return redirect('panel_actividades')


    return redirect('panel_actividades')

