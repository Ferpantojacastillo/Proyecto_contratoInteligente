from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class Usuario(AbstractUser):
    username_validator = RegexValidator(
        regex=r'^[\w\s\-áéíóúñÁÉÍÓÚÑ]+$',
        message='El nombre de usuario solo puede contener letras, números, espacios y guiones.',
        code='invalid_username'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        help_text='Letras, números, espacios y guiones. Sin caracteres especiales.'
    )

    es_admin_creditos = models.BooleanField(default=False)
    es_alumno = models.BooleanField(default=True)
    es_docente = models.BooleanField(default=False)
    numero_control = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.username


