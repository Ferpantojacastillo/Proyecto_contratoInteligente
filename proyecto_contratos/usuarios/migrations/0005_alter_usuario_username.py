 

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_add_numero_control'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='username',
            field=models.CharField(
                help_text='Letras, números, espacios y guiones. Sin caracteres especiales.',
                max_length=150,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        code='invalid_username',
                        message='El nombre de usuario solo puede contener letras, números, espacios y guiones.',
                        regex='^[\\w\\s\\-áéíóúñÁÉÍÓÚÑ]+$'
                    )
                ],
            ),
        ),
    ]
