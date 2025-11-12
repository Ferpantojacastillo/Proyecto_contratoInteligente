 
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('creditos', '0003_credito_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='credito',
            name='numero_control',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
