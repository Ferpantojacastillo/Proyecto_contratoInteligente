 

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actividades', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='actividad',
            name='capacidad',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='actividad',
            name='creado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actividades_creadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='actividad',
            name='creditos_equivalentes',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='actividad',
            name='descripcion',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='actividad',
            name='inscritos',
            field=models.ManyToManyField(blank=True, related_name='actividades_inscritas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='actividad',
            name='lugar',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='fecha',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='nombre',
            field=models.CharField(max_length=150),
        ),
    ]
