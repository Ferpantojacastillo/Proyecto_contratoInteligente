from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Actividad
from .forms import ActividadForm
from creditos.models import Credito
from usuarios.models import Usuario
from django.urls import reverse
from django.utils import timezone


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
    return render(request, 'actividades/detalle.html', {
        'actividad': actividad,
        'esta_inscrito': esta_inscrito
    })


@login_required
def inscribirse(request, id_actividad):
    actividad = get_object_or_404(Actividad, id=id_actividad)

    if actividad.capacidad and actividad.inscritos.count() >= actividad.capacidad:
        messages.error(request, "Capacidad llena.")
        return redirect('detalle_actividad', id_actividad=id_actividad)

    actividad.inscritos.add(request.user)
    messages.success(request, "Te inscribiste correctamente.")
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

