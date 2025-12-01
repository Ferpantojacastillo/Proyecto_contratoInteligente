from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.text import slugify
from .models import Usuario


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
        user.es_alumno = True
        user.es_docente = False
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


class DocenteRegistroForm(forms.ModelForm):
    """Form para crear un docente. El username y la contraseña se generarán
    automáticamente en la vista; aquí solo se aceptan nombre, email y número.
    """
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'numero_control']
        labels = {
            'username': 'Nombre completo',
            'email': 'Correo electrónico',
            'numero_control': 'Número de control',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'numero_control': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        docente = super().save(commit=False)
        docente.es_docente = True
        docente.es_alumno = False
        if commit:
            docente.save()
        return docente
