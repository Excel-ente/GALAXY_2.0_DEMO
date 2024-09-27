from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from administracion.models import Configuracion

class Command(BaseCommand):
    help = 'Configura el proyecto inicializando la base de datos y creando un superusuario.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Inicializando la base de datos...'))
        call_command('migrate')

        self.stdout.write(self.style.SUCCESS('Creando un superusuario...'))
        User = get_user_model()
        if not User.objects.filter(username='EXCEL-ENTE').exists():
            username = 'EXCEL-ENTE'
            email = 'admin@example.com'
            password = 'Galaxy123.'
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {username} / {password}'))
        else:
            self.stdout.write(self.style.WARNING('El superusuario ya existe.'))

        self.stdout.write(self.style.SUCCESS('Verificando configuración inicial...'))
        if not Configuracion.objects.filter(id=1).exists():
            Configuracion.objects.create(
                nombre='Mi Empresa',
                direccion='Mi direccion de ejemplo 3216, Buenos aires',
                telefono='123456789',
                redes='@miempresa',
                cuit='20-12345678-9',
                moneda='$',
                moneda_secundaria='USD',
            )
            self.stdout.write(self.style.SUCCESS('Configuración inicial creada.'))
        else:
            self.stdout.write(self.style.WARNING('La configuración inicial ya existe.'))

        self.stdout.write(self.style.SUCCESS('Configuración del proyecto completada.'))
