 

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creditos', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='credito',
            name='nombre',
            field=models.CharField(default='', max_length=100),
        ),
    ]
