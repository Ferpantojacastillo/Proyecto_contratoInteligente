 
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('creditos', '0004_credito_numero_control'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SolicitudCredito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('tipo', models.CharField(choices=[('academico', 'Académico'), ('cultural', 'Cultural'), ('deportivo', 'Deportivo')], max_length=20)),
                ('semestre', models.CharField(max_length=10)),
                ('numero_control', models.CharField(blank=True, max_length=30)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], default='pendiente', max_length=20)),
                ('revisado_en', models.DateTimeField(blank=True, null=True)),
                ('comentario', models.TextField(blank=True)),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solicitudes_credito', to=settings.AUTH_USER_MODEL)),
                ('revisado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solicitudes_revisadas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
