from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.forms import PasswordInput
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .models import Usuario


class UsuarioAdminForm(forms.ModelForm):
    # Campo auxiliar para que el administrador pueda introducir
    # una contraseña en texto plano al crear/editar un usuario.
    raw_password = forms.CharField(
        label='Contraseña (texto plano)',
        required=False,
        widget=PasswordInput(attrs={'class': 'form-control'}),
        help_text='Si rellenas este campo, la contraseña será hasheada automáticamente.'
    )
    class Meta:
        model = Usuario
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo 'password' opcional si existe (puede no estar en fieldsets personalizados)
        if 'password' in self.fields:
            self.fields['password'].required = False

    def save(self, commit=True):
        # Asegurar que si el administrador introduce una contraseña en texto
        # plano en el campo `password`, se convierta a hash con `set_password`.
        user = super().save(commit=False)
        # Primero, si el admin usó el campo auxiliar `raw_password`, priorizarlo.
        raw = self.cleaned_data.get('raw_password')
        if raw:
            user.set_password(raw)
        else:
            # Compatibilidad con posibles usos del campo `password` en el formulario:
            pwd = self.cleaned_data.get('password')
            # Si hay una contraseña y no parece ya estar hasheada (no contiene '$'),
            # usar `set_password` para guardarla correctamente.
            if pwd and '$' not in pwd:
                user.set_password(pwd)
        if commit:
            user.save()
        return user


@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    form = UsuarioAdminForm
    add_form = UsuarioAdminForm

    list_display = (
        'username', 'email', 'numero_control',
        'es_admin_creditos', 'es_docente', 'es_alumno', 'is_staff', 'is_active'
    )

    list_filter = (
        'es_admin_creditos', 'es_docente', 'es_alumno', 'is_staff', 'is_active'
    )

    # Fieldsets para edición de usuarios existentes
    fieldsets = (
        ('Datos básicos', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'raw_password')
        }),
        ('Información adicional del usuario', {
            'fields': ('numero_control', 'es_admin_creditos', 'es_docente', 'es_alumno')
        }),
        ('Permisos', {
            'fields': ('is_staff', 'is_superuser', 'is_active', 'groups')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    # Fieldsets para crear nuevos usuarios (sin campos de fecha que se generan automáticamente)
    add_fieldsets = (
        ('Datos básicos', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'raw_password'),
            'description': 'Rellena el campo "Contraseña (texto plano)" con la contraseña que quieras asignar.'
        }),
        ('Información adicional', {
            'fields': ('numero_control', 'es_admin_creditos', 'es_docente', 'es_alumno')
        }),
        ('Permisos', {
            'fields': ('is_staff', 'is_superuser', 'is_active')
        }),
    )

    actions = ['activar_docentes', 'desactivar_docentes']

    def activar_docentes(self, request, queryset):
        """Acción para activar cuentas de docentes seleccionadas."""
        actualizado = queryset.filter(es_docente=True, is_active=False).update(is_active=True)
        self.message_user(request, f'{actualizado} cuenta(s) docente(s) activada(s) exitosamente.')
    activar_docentes.short_description = 'Activar cuentas docentes seleccionadas'

    def desactivar_docentes(self, request, queryset):
        """Acción para desactivar cuentas de docentes seleccionadas."""
        actualizado = queryset.filter(es_docente=True, is_active=True).update(is_active=False)
        self.message_user(request, f'{actualizado} cuenta(s) docente(s) desactivada(s).')
    desactivar_docentes.short_description = 'Desactivar cuentas docentes seleccionadas'

    def save_model(self, request, obj, form, change):
        # Si es docente y se está creando por primera vez
        if obj.es_docente and not change:
            # Si el administrador ya proporcionó una contraseña en el formulario
            # (campo auxiliar `raw_password`), respetarla; en caso contrario,
            # generar una contraseña aleatoria y asignarla.
            provided = None
            try:
                provided = form.cleaned_data.get('raw_password')
            except Exception:
                provided = None

            if provided:
                obj.set_password(provided)
                generated_pwd = provided
            else:
                generated_pwd = get_random_string(12)
                obj.set_password(generated_pwd)
            # Asegurar que la cuenta quede activa para que el docente pueda
            # iniciar sesión inmediatamente con las credenciales mostradas.
            obj.is_active = True

            messages.success(request, f'Contraseña docente: {generated_pwd} (cópiala ahora, se mostrará solo una vez).')

            if obj.email:
                subject = 'Acceso al Portal Docente'
                login_url = getattr(settings, 'SITE_URL', '') + '/login/'
                message = (
                    f'Hola {obj.username},\n\n'
                    f'Se creó tu acceso al portal docente.\n\n'
                    f'Usuario: {obj.username}\n'
                    f'Contraseña: {generated_pwd}\n\n'
                    f'Accede aquí: {login_url}'
                )

                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [obj.email])
                    messages.info(request, f'Se envió la contraseña al correo: {obj.email}')
                except Exception as e:
                    messages.error(request, f"No se pudo enviar correo: {e}")

        super().save_model(request, obj, form, change)


