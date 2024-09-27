from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Configuracion, medioDePago

@receiver(post_save, sender=Configuracion)
def crear_metodos_pago(sender, instance, created, **kwargs):
    if created:
        metodos_pago = ["Efectivo", "Cuenta Corriente", "Transferencia"]
        for metodo in metodos_pago:
            if not medioDePago.objects.filter(Nombre=metodo).exists():
                medioDePago.objects.create(Nombre=metodo)
