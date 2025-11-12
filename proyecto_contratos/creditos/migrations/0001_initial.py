 

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Credito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('academico', 'Académico'), ('cultural', 'Cultural'), ('deportivo', 'Deportivo')], max_length=20)),
                ('semestre', models.CharField(max_length=10)),
                ('fecha_liberacion', models.DateField(blank=True, null=True)),
                ('liberado', models.BooleanField(default=False)),
                ('firmado_alumno', models.BooleanField(default=False)),
                ('firmado_admin', models.BooleanField(default=False)),
            ],
        ),
    ]
