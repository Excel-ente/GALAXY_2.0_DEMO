# Generated by Django 5.0.6 on 2024-06-29 13:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0024_alter_compras_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='FECHA_ENTREGA',
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
    ]
