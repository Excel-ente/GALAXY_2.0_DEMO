# Generated by Django 4.1.5 on 2024-02-17 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0014_alter_insumo_unidad_medida_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='insumoinsumocompuesto',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]
