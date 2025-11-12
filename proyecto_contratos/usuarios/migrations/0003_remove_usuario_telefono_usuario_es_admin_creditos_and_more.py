 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_remove_usuario_rol_usuario_telefono'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='telefono',
        ),
        migrations.AddField(
            model_name='usuario',
            name='es_admin_creditos',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='usuario',
            name='es_alumno',
            field=models.BooleanField(default=True),
        ),
    ]
