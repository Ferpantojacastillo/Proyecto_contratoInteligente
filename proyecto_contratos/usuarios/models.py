from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password

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


    docente_password = models.CharField(
        max_length=128,
        blank=True,
        help_text='Contraseña del docente (hash).'
    )

    def __str__(self):
        return self.username

   
    def set_docente_password(self, raw_password):
        if raw_password:
          
            self.docente_password = make_password(raw_password)

          
            self.password = make_password(raw_password)
        else:
            self.docente_password = ''

 
    def check_docente_password(self, raw_password):
        if not self.docente_password:
            return False
        return check_password(raw_password, self.docente_password)

 
    def save(self, *args, **kwargs):
     
        if (
            self.docente_password
            and not self.docente_password.startswith("pbkdf2_")
        ):
        
            self.password = make_password(self.docente_password)
            self.docente_password = make_password(self.docente_password)

        super().save(*args, **kwargs)
