# Generated by Django 4.1.5 on 2024-02-15 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0010_remove_insumocompuestoreceta_precio_unitario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracion',
            name='mostrar_stock_pendiente',
            field=models.BooleanField(default=True),
        ),
    ]
