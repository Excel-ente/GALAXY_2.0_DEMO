# Generated by Django 5.0.6 on 2024-06-29 12:25

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0022_alter_insumo_rentabilidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insumocompuesto',
            name='UNIDADES_RESULTANTES',
            field=models.PositiveIntegerField(default=1, verbose_name='PORCIONES RESULTANTES'),
        ),
        migrations.CreateModel(
            name='Fabrica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FECHA', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('ESTADO', models.CharField(choices=[('Pendiente', 'Pendiente'), ('En proceso', 'En proceso'), ('Finalizado', 'Finalizado')], default='Pendiente', max_length=20)),
                ('UNIDADES_RESULTANTES', models.PositiveIntegerField(default=1, verbose_name='PORCIONES RESULTANTES')),
                ('VALIDO_HASTA', models.DateField(blank=True, null=True)),
                ('RECETA', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administracion.insumocompuesto')),
            ],
            options={
                'verbose_name': 'Lote',
                'verbose_name_plural': 'Fabricaciones',
            },
        ),
    ]
