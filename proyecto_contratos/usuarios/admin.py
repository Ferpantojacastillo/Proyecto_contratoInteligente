from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .models import Usuario


class UsuarioAdminForm(forms.ModelForm):
    docente_password_plain = forms.CharField(
        label='Contraseña docente (asignar manualmente)',
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text='Se guardará encriptada y también será la contraseña principal del docente.'
    )

    generar_docente_password = forms.BooleanField(
        label='Generar contraseña automática',
        required=False,
        help_text='Si se marca, el sistema generará una contraseña segura y la mostrará solo una vez.'
    )

    class Meta:
        model = Usuario
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)

        pwd_manual = self.cleaned_data.get('docente_password_plain')
        generar = self.cleaned_data.get('generar_docente_password')

        # Si se generará automáticamente, ignoramos cualquier contraseña manual
        if generar:
            pwd_manual = None

        # Si el admin escribió una contraseña manual
        if pwd_manual:
            user.set_docente_password(pwd_manual)

        if commit:
            user.save()

        # Limpiar los campos del formulario después de guardar
        self.cleaned_data['docente_password_plain'] = ''
        self.cleaned_data['generar_docente_password'] = False

        return user


@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    form = UsuarioAdminForm

    list_display = (
        'username', 'email', 'numero_control',
        'es_admin_creditos', 'es_docente', 'es_alumno', 'is_staff'
    )

    list_filter = (
        'es_admin_creditos', 'es_docente', 'es_alumno', 'is_staff'
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional del usuario', {
            'fields': (
                'numero_control',
                'es_admin_creditos',
                'es_docente',
                'es_alumno',
                'docente_password_plain',
                'generar_docente_password',
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
                'docente_password_plain',
                'generar_docente_password',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        generar = form.cleaned_data.get('generar_docente_password')
        generated_pwd = None

        # Si el admin marcó generar contraseña automática
        if generar and obj.es_docente:
            generated_pwd = get_random_string(12)
            obj.set_docente_password(generated_pwd)

        super().save_model(request, obj, form, change)

        # Mostrar la contraseña generada solo una vez
        if generated_pwd:
            messages.success(request, f'Contraseña docente generada: {generated_pwd} (cópiala ahora, se mostrará solo una vez).')

            # Intentar enviar correo si el docente tiene email
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
