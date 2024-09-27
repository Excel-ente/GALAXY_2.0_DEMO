from django.contrib import admin
from django.contrib import messages
from .models import  DetalleCompra,Configuracion,Insumo


@admin.action(description="Aceptar Presupuesto")
def Aceptar(modeladmin, request, queryset):
    for receta in queryset:
        if receta.check_pagos():
            if receta.ESTADO == "Pendiente":
                receta.ESTADO = "Aceptado"
                receta.save()
            else:
                messages.warning(request, f"No se puede aceptar el pedido porque no es un pedido pendiente.")
        else:
            messages.warning(request, f"La suma de los pagos no coincide con el total del presupuesto.")

@admin.action(description="Entregar Pedido")
def Entregar(modeladmin, request, queryset):
    for receta in queryset:
        if receta.ESTADO == "Aceptado":
            receta.ESTADO = "Entregado"        
            receta.save()
        else:
            messages.warning(request, f"Para entregar el pedido debe haberse aceptado el presupuesto.")

@admin.action(description="Confirmar Compra")
def ConfirmarCompra(modeladmin, request, queryset):
    for compra in queryset:

        if compra.check_pagos() == True:


            if compra.ESTADO == False:

                compra.ESTADO = True
                compra.save()

                productos = DetalleCompra.objects.filter(COMPRA=compra)

                for producto in productos:
                    if producto.ActualizarCosto:
                        
                        item = Insumo.objects.filter(id=producto.PRODUCTO.pk).first()

                        # Primero capturo precio anterior
                        costo_anterior = float(producto.PRODUCTO.costo_unitario())
                        nuevo_costo = float(producto.PRECIO) - float(float(producto.PRECIO) * float(producto.DESCUENTO) / 100)

                        if nuevo_costo > costo_anterior:
                            item.PRECIO_COMPRA = float(nuevo_costo) * float(item.CANTIDAD) #si hay mas cantidad, debo multiplicar el costo por la cantidad
                        else:
                            if Configuracion.objects.first().pisar_costo_inferior == False:
                                item.PRECIO_COMPRA = float(nuevo_costo) * float(item.CANTIDAD)

                        item.PROVEEDOR = producto.COMPRA.PROVEEDOR
                        item.save()

                messages.success(request, f"N° Compra {compra.id} Confirmada correctamente.")
            else:
                messages.warning(request, f"La compra #{compra.id} ya se encuentra confirmada.")

        else:
            messages.warning(request, f"La suma de pagos no coincide con el total de compra.")
