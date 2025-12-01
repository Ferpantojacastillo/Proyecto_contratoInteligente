from django.db import models
from usuarios.models import Usuario

class Credito(models.Model):
    TIPOS = (
        ('academico', 'Académico'),
        ('cultural', 'Cultural'),
        ('deportivo', 'Deportivo'),
    )

    alumno = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='creditos')
    nombre = models.CharField(max_length=100, default="") 
    tipo = models.CharField(max_length=20, choices=TIPOS)
    semestre = models.CharField(max_length=10)
    numero_control = models.CharField(max_length=30, blank=True)
    fecha_liberacion = models.DateField(blank=True, null=True)
    liberado = models.BooleanField(default=False)
    firmado_alumno = models.BooleanField(default=False)
    firmado_admin = models.BooleanField(default=False)
    firmado_docente = models.BooleanField(default=False)
    firmado_admin_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='creditos_firmados_admin')
    firmado_admin_en = models.DateTimeField(null=True, blank=True)
    firmado_docente_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='creditos_firmados_docente')
    firmado_docente_en = models.DateTimeField(null=True, blank=True)
    firmado_alumno_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='creditos_firmados_alumno')
    firmado_alumno_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.alumno.username} - {self.tipo} ({'Liberado' if self.liberado else 'Pendiente'})"


class SolicitudCredito(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )

    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes_credito')
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=Credito.TIPOS)
    semestre = models.CharField(max_length=10)
    numero_control = models.CharField(max_length=30, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    revisado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_revisadas')
    revisado_en = models.DateTimeField(null=True, blank=True)
    comentario = models.TextField(blank=True)

    def __str__(self):
        return f"Solicitud {self.id} - {self.nombre} - {self.alumno.username} ({self.estado})"




 
