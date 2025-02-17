# Generated by Django 5.0.7 on 2024-09-16 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0034_alter_compras_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='COSTOS_TOTALES',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='pedido',
            name='INGRESOS_TOTALES',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='compras',
            name='FECHA',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
