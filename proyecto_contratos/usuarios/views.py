from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm
from .forms import DocenteRegistroForm
from django.conf import settings
from creditos.models import Credito
from actividades.models import Actividad
from django.db.models import Q


@login_required
def perfil(request):
    numero = request.user.numero_control or ''
    nombre_usuario = request.user.get_full_name() or request.user.username

    creditos = Credito.objects.filter(liberado=True).filter(
        Q(alumno=request.user) | Q(numero_control=numero) | Q(nombre__icontains=nombre_usuario)
    ).distinct()
    total = creditos.count()
    progreso = int((total / 5) * 100) if total <= 5 else 100
    actividades = Actividad.objects.order_by('fecha')[:10]

    return render(request, 'usuarios/perfil.html', {
        'creditos': creditos,
        'total': total,
        'progreso': progreso,
        'actividades': actividades,
    })


@login_required
def inicio(request):
    if request.user.is_staff or request.user.es_admin_creditos:
        return redirect('panel_actividades')
    else:
        return redirect('perfil')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Por favor inicia sesión.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def docente_registro(request):
    # Registro exclusivo para docentes mediante invite code
    if request.method == 'POST':
        form = DocenteRegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de docente exitoso. Ahora puedes acceder al portal docente.')
            return redirect('docente_login')
    else:
        form = DocenteRegistroForm()
    return render(request, 'usuarios/docente_registro.html', {'form': form})





