# Generated by Django 4.1.5 on 2024-02-19 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0017_alter_pagospedidos_medio_de_pago'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientereceta',
            name='cantidad',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=20),
        ),
        migrations.AlterField(
            model_name='insumocompuestoreceta',
            name='cantidad',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=20),
        ),
    ]
