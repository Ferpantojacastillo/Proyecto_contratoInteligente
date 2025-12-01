from django.db import models
from usuarios.models import Usuario
from creditos.models import Credito

class Actividad(models.Model):
    TIPOS = (
        ('academico', 'Académico'),
        ('cultural', 'Cultural'),
        ('deportivo', 'Deportivo'),
    )
    nombre = models.CharField(max_length=150)
    convo = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha = models.DateTimeField()
    lugar = models.CharField(max_length=150, blank=True)
    creditos_equivalentes = models.PositiveSmallIntegerField(default=1)
    capacidad = models.PositiveIntegerField(blank=True, null=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='actividades_creadas')
    inscritos = models.ManyToManyField(Usuario, blank=True, related_name='actividades_inscritas')
    liberado = models.BooleanField(default=False)
    liberado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='actividades_liberadas')
    fecha_liberacion = models.DateTimeField(null=True, blank=True)
    encargado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='actividades_encargadas')

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()}) - {'Liberada' if self.liberado else 'Pendiente'}"

