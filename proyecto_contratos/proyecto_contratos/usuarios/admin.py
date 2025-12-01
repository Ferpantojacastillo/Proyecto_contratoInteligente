from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .models import Usuario


class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

    def save(self, commit=True):
        # Asegurar que si el administrador introduce una contraseña en texto
        # plano en el campo `password`, se convierta a hash con `set_password`.
        user = super().save(commit=False)
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

    list_display = (
        'username', 'email', 'numero_control',
        'es_admin_creditos', 'es_docente', 'es_alumno', 'is_staff', 'is_active'
    )

    list_filter = (
        'es_admin_creditos', 'es_docente', 'es_alumno', 'is_staff', 'is_active'
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional del usuario', {
            'fields': (
                'numero_control',
                'es_admin_creditos',
                'es_docente',
                'es_alumno',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': (
                'numero_control',
                'es_admin_creditos',
                'es_docente',
                'es_alumno',
            )
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
            generated_pwd = get_random_string(12)
            obj.set_password(generated_pwd)

            messages.success(request, f'Contraseña docente generada: {generated_pwd} (cópiala ahora, se mostrará solo una vez).')

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


