from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistroForm, LoginForm, DocenteRegistroForm
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
            user = form.get_user()
            login(request, user)
            return redirect('inicio')
    else:
        form = LoginForm()
    return render(request, 'usuarios/docente_login.html', {'form': form})


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
    if request.method == 'POST':
        form = DocenteRegistroForm(request.POST)
        if form.is_valid():
            docente = form.save(commit=False)

            # Generar credenciales automáticas
            generated_pwd = get_random_string(12)

            # Generar un username único basado en el nombre (slug) + sufijo aleatorio si hace falta
            from django.utils.text import slugify
            base = slugify(docente.username or 'docente')[:30]
            candidate = base
            from usuarios.models import Usuario as UsuarioModel
            suffix_attempt = 0
            while UsuarioModel.objects.filter(username=candidate).exists():
                suffix_attempt += 1
                candidate = f"{base[: max(1, 28 - len(str(suffix_attempt)))]}-{suffix_attempt}"

            docente.username = candidate
            docente.set_password(generated_pwd)
            docente.es_docente = True
            docente.es_alumno = False
            # Dejar la cuenta inactiva para que NO pueda iniciar sesión hasta activación manual
            docente.is_active = False
            docente.save()

            # Store credentials in session to display on confirmation page
            request.session['docente_username'] = docente.username
            request.session['docente_password'] = generated_pwd
            request.session['docente_email'] = docente.email or ''

            # Enviar correo si existe el email (opcional)
            if docente.email:
                subject = 'Acceso al Portal Docente (creado, cuenta inactiva)'
                login_url = getattr(settings, 'SITE_URL', '') + '/docente/login/'
                message = (
                    f'Hola {docente.username},\n\n'
                    f'Se creó tu cuenta de docente (actualmente INACTIVA).\n\n'
                    f'Usuario: {docente.username}\n'
                    f'Contraseña: {generated_pwd}\n\n'
                    f'Nota: La cuenta ha sido creada pero no está activa. Un administrador debe activarla antes de que puedas iniciar sesión.\n\n'
                    f'Accede aquí cuando esté activada: {login_url}'
                )
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [docente.email])
                    messages.info(request, f'Se envió notificación al correo: {docente.email}')
                except Exception as e:
                    messages.error(request, f"No se pudo enviar correo: {e}")

            return redirect('docente_credenciales')
    else:
        form = DocenteRegistroForm()
    return render(request, 'usuarios/docente_registro.html', {'form': form})


def docente_credenciales(request):
    """Página que muestra las credenciales generadas para el docente recién registrado."""
    username = request.session.pop('docente_username', None)
    password = request.session.pop('docente_password', None)
    email = request.session.pop('docente_email', '')

    if not username or not password:
        messages.error(request, 'No hay credenciales para mostrar. Por favor, registrate nuevamente.')
        return redirect('docente_registro')

    return render(request, 'usuarios/docente_credenciales.html', {
        'username': username,
        'password': password,
        'email': email,
    })
