from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario
from django.conf import settings

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'numero_control']
        labels = {
            'username': 'Nombre completo',
            'email': 'Correo electrónico',
            'numero_control': 'Número de control',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Fernanda Pantoja',
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero_control': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError('La contraseña es requerida.')
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise forms.ValidationError('Debes confirmar tu contraseña.')
        return password2

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        nc = self.cleaned_data.get('numero_control')
        if nc:
            user.numero_control = nc
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        label='Nombre de usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label='Contraseña'
    )


class DocenteRegistroForm(RegistroForm):
    docente_password1 = forms.CharField(
        label='Contraseña docente',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    docente_password2 = forms.CharField(
        label='Confirmar contraseña docente',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    invite_code = forms.CharField(
        label='Código de registro docente',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Introduce el código que te proporcionó el administrador.'
    )

    class Meta(RegistroForm.Meta):
        fields = ['username', 'email', 'numero_control']

    def clean(self):
        cleaned = super().clean()
        dp1 = cleaned.get('docente_password1')
        dp2 = cleaned.get('docente_password2')
        invite = cleaned.get('invite_code')

        if not invite or invite != getattr(settings, 'DOCENTE_INVITE_CODE', None):
            raise forms.ValidationError('Código de registro docente inválido.')

        if not dp1 or not dp2 or dp1 != dp2:
            raise forms.ValidationError('Las contraseñas docentes no coinciden.')

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
     
        user.es_docente = True
    
        user.set_docente_password(self.cleaned_data['docente_password1'])

        user.set_unusable_password()
        if commit:
            user.save()
        return user
