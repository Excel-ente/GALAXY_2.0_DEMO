# Generated by Django 5.0.7 on 2024-09-15 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0032_insumocompuesto_precio_venta_unitario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insumocompuesto',
            name='PRECIO_VENTA_UNITARIO',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20),
        ),
    ]
