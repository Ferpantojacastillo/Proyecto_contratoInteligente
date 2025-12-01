 
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('tipo', models.CharField(choices=[('academico', 'Académico'), ('cultural', 'Cultural'), ('deportivo', 'Deportivo')], max_length=20)),
                ('fecha', models.DateField()),
            ],
        ),
    ]
