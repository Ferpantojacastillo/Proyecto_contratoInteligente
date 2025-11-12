 
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_remove_usuario_telefono_usuario_es_admin_creditos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='numero_control',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
