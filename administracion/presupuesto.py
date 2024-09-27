from django.http import HttpResponse
from reportlab.lib.pagesizes import legal
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from django.contrib import admin, messages
from administracion.models import ComentarioVenta, Configuracion, PagosPedidos, ingredientereceta, insumoCompuestoReceta
import os
from django.db import models

@admin.action(description="Descargar Presupuesto")
def generar_presupuesto(modeladmin, request, queryset):

    subtotal_compra = 0
    total=0

    if len(queryset) != 1:
        messages.error(request, "Seleccione solo un pedido para generar el presupuesto.")
        return
        
    # Obtener dato de la venta
    venta = queryset[0]
    config = Configuracion.objects.first()
    current_directory = os.getcwd()

    #if venta.ESTADO == "Pendiente":

    # Obtener datos de la empresa
    nombre_empresa = config.nombre
    direccion_empresa = config.direccion
    telefono_empresa = config.telefono
    email_empresa = str(config.redes)
    descuentos_insumos=0
    numero_item = 1

    #Crear el objeto
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{venta.id}.pdf"'

    # Crear el lienzo PDF
    p = canvas.Canvas(response, pagesize=legal)

    # Agregar contenido al lienzo
    y = 950  # Posición vertical inicial
    x = 50
    # Color de fondo del reporte
    color_1=220/256 # <-- por definicion tengo que poner el valor rgb en %, es decir valor_rgb/256
    color_2=220/256
    color_3=220/256
    p.setFillColorRGB(color_1, color_2, color_3)
    p.rect(0, 0, 2000, 2000, fill=True)

    # RECTANGULO SIPERIOR
    p.setFillColorRGB(200, 200, 200)  # Color de fondo gris claro
    p.setStrokeColorRGB(255, 255, 255)  # Color del borde blanco
    p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    p.rect(30, 870, 360, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco
    p.rect(400, 870, 180, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco


    if config.imagen:
        logo_path = config.imagen.path
    else:
        logo_path = os.path.join(current_directory, 'logo.png')

    # Verificar si el archivo de imagen del logo existe
    if logo_path:
        # Tamaño y posición del logo
        logo_width = 100  # Ancho del logo
        logo_height = 100 # Alto del logo
        logo_x = 440  # Posición horizontal del logo
        logo_y = 875  # Posición vertical del logo

        # Agregar el logo al lienzo PDF
        logo_image = ImageReader(logo_path)
        p.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)
    

    # RECTANGULO SIPERIOR
    p.setStrokeColorRGB(255, 255, 255)  # Color del borde blanco
    p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    p.rect(30, 750, 550, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    # Escribir el nombre de la empresa encima del fondo gris
    p.setFillColorRGB(0, 0, 0) 
    p.setFont("Helvetica-Bold", 18)  
    p.drawString(x, y, nombre_empresa)
    y -= 25

    p.setFont("Helvetica", 12)  # Fuente normal
    p.drawString(x, y, direccion_empresa)
    y -= 18
    p.drawString(x, y, telefono_empresa)
    y -= 18
    p.drawString(x, y, email_empresa)
    y -= 18

    if True:

        # Seccion de la izquierda (datos de la venta) --------->
        y = 841
        
        p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x - 10, y, f"DATOS DE LA VENTA")
        y -= 20

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Numero venta: ")
        p.setFont("Helvetica", 10)
        codigo_str = str(venta.id)
        p.drawString(122, y, codigo_str.zfill(4))
        y -= 20

        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Fecha: ")
        p.setFont("Helvetica", 10)  # Fuente normal
        fecha = venta.FECHA.strftime("%H:%M %d/%m/%Y")
        p.drawString(90, y, fecha)
        y -= 20


        # Seccion de la derecha (datos del cliente) --------->
        y = 841

        p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x + 220, y, f"DATOS DEL CLIENTE")
        p.setFillColorRGB(0, 0, 0)
        y -= 20

        if venta.CLIENTE:

            p.setFont("Helvetica-Bold", 10)
            p.drawString(x + 250, y, "Cliente:")
            p.setFont("Helvetica", 10)  # Fuente normal
            p.drawString(x + 310, y, f'{venta.CLIENTE}')
            y -= 20

            p.setFont("Helvetica-Bold", 10)
            p.drawString(x + 250, y, "Direccion:")
            p.setFont("Helvetica", 10)  # Fuente normal
            p.drawString(x + 310, y, f'{venta.CLIENTE.DIRECCION}')
            y -= 20

            p.setFont("Helvetica-Bold", 10)
            p.drawString(x + 250, y, "Telefono:")
            p.setFont("Helvetica", 10)  # Fuente normal
            p.drawString(x + 310, y, f'{venta.CLIENTE.TELEFONO}')


        else:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x + 250, y, "Cliente:")
            p.setFont("Helvetica", 10)  # Fuente normal
            p.drawString(90, x + 310, f'Consumidor Final')
            y -= 20

    y -= 35

    productos = ingredientereceta.objects.filter(receta=venta)
    p.setFillColorRGB(1,1,1)
    p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    p.rect(30, 240, 550, 500, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    p.setFillColorRGB(1,1,1)
    p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    p.rect(30, 140, 550, 90, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco
    y -= 20

    if productos:
        p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x - 10, y - 5, f"PRODUCTOS INCLUIDOS EN EL PRESUPUESTO ({productos.count():,.2f})")
        y -= 20

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "NOMBRE DE PRODUCTO")
        p.drawString(x + 170, y, "CANTIDAD")
        p.drawString(x + 255, y, "P. UNITARIO")
        p.drawString(x + 370, y, "DESC")
        p.drawString(x + 450, y, "SUBTOTAL")
        y -=20

        numero_item  = 1
        for producto in productos:

            p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x - 16, y, f"{numero_item}")
            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 10)

            nombre_producto = f"{producto.producto.PRODUCTO}"
            p.drawString(x, y, f"{str(nombre_producto).upper()}")
            p.drawString(x + 180, y, f"{producto.cantidad} {producto.producto.UNIDAD_MEDIDA[:3]}")
            precio=float(producto.producto.precio_venta())
            precio_total=(float(precio) * float(producto.cantidad) - float(producto.descuento))
            p.drawString(x + 255, y, f"{config.moneda} {precio:,.2f}")
            p.drawString(x + 350, y, f"{config.moneda} {producto.descuento:,.2f}")
            p.drawString(x + 450, y, f"{config.moneda} {precio_total:,.2f}")

            descuentos_insumos += float(producto.descuento)
            numero_item += 1
            y -= 15
        y -= 10
    insumos_compuestos = insumoCompuestoReceta.objects.filter(pedido=venta)
    

    if insumos_compuestos:
        p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x - 10, y - 5, f"PRODUCTOS COMPUESTOS INCLUIDOS EN EL PRESUPUESTO ({insumos_compuestos.count():,.2f})")
        y -= 30

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "NOMBRE DE PRODUCTO")
        p.drawString(x + 200, y, "CANTIDAD")
        p.drawString(x + 300, y, "P. UNITARIO")
        p.drawString(x + 460, y, "SUBTOTAL")
        y -=20

        numero_item  = 1
        for producto in insumos_compuestos:

            p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x - 16, y, f"{numero_item}")
            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 10)

            nombre_producto = f"{producto.insumo_Compuesto}"
            p.drawString(x, y, f"{nombre_producto}")
            p.drawString(x + 245, y, f"{producto.cantidad} Uni")
            precio=float(producto.insumo_Compuesto.precio_unitario())
            precio_total=float(producto.insumo_Compuesto.precio_unitario()) * float(producto.cantidad)
            p.drawString(x + 340, y, f"{config.moneda} {precio:,.2f}")
            p.drawString(x + 440, y, f"{config.moneda} {precio_total:,.2f}")

            numero_item += 1
            y -=  15

    y = 220
    comentarios=ComentarioVenta.objects.filter(VENTA=venta)
    if comentarios:

        # Bloque entrega
        p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x + 240, y - 5, f"COMENTARIOS")
        y -= 20

        for comentario in comentarios:
            p.setFillColorRGB(1, 0, 0)
            p.setFont("Helvetica", 10)
            fecha_comentario = comentario.FECHA.strftime("%Y-%m-%d")# %H:%M
            p.drawString(x + 250, y, fecha_comentario)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(x + 315, y, comentario.COMENTARIO )
            y -= 10


    # RECTANGULO PRODUCTOS
    p.setFillColorRGB(1,1,1)
    p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    p.rect(30, 20, 550, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    y = 120
    medios_de_pago_select = PagosPedidos.objects.filter(PEDIDO=venta)
    
    pagos=0
    if medios_de_pago_select:
        # Bloque entrega
        p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x - 10, y - 5, f"PAGOS DEL CLIENTE")
        y -= 20

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "MEDIO DE PAGO")
        p.drawString(x + 150, y, "TOTAL")

        y -=20

        numero_item  = 1

        for pago in medios_de_pago_select:
            
            p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x - 16, y, f"{numero_item}")
        
            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 10)
            p.drawString(x, y, f"{pago.MEDIO_DE_PAGO}")
            p.drawString(x + 150, y, f"{config.moneda} {(pago.TOTAL):,.2f}")
            if pago.MEDIO_DE_PAGO.Nombre != "Cuenta Corriente":
                pagos += pago.TOTAL
                
            numero_item += 1
            y -=  10

        if float(venta.DESCUENTO) > 0:
            p.setFillColorRGB(1, 0, 0)
            p.setFont("Helvetica", 10)
            p.drawString(x, y, f"Descuentos Adicionales: ")
            p.drawString(x + 150, y, f"{config.moneda} {venta.DESCUENTO:,.2f}")
            y -=  10

        if float(descuentos_insumos) > 0:
            p.setFont("Helvetica", 10)
            p.drawString(x, y, f"Descuentos por producto: ")
            p.drawString(x + 150, y, f"{config.moneda} {descuentos_insumos:,.2f}")
            p.setFillColorRGB(0, 0, 0)
            y -=  10

    # seccion final de pacgos
    pie=True
    if pie:
        y = 110
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 13)
        p.drawString(320, y, "Total Presupuestado: ")
        p.setFillColorRGB(1, 0, 0)
        p.setFont("Helvetica", 13)  # Fuente normal
        subtotal_sin_desc = float(venta.precio_total()) + float(venta.DESCUENTO) + float(descuentos_insumos)
        p.drawString(465, y, f"{config.moneda} {subtotal_sin_desc:,.2f}")

        y -= 20

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 13)
        p.drawString(320, y, "Descuentos: ")
        p.setFillColorRGB(1, 0, 0)
        p.setFont("Helvetica", 13)  # Fuente normal

        descuentos = float(venta.DESCUENTO) + descuentos_insumos
        if descuentos > 0:
            p.drawString(465, y, f"{config.moneda} {descuentos:,.2f}")
        else:
            p.drawString(465, y, f"{config.moneda} {0:,.2f}")
        y -= 20

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 13)
        p.drawString(320, y, "Suma de Pagos: ")
        p.setFillColorRGB(1, 0, 0)
        p.setFont("Helvetica", 13)  # Fuente normal
        p.drawString(465, y, f"{config.moneda} {pagos:,.2f}")

        y -= 30

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(320, y, "PENDIENTE: ")
        p.setFillColorRGB(1, 0, 0)
        p.setFont("Helvetica", 16)
        total_bruto = float(venta.precio_total()) - float(pagos)
        p.drawString(450, y, f"{config.moneda} {total_bruto:,.2f}")


    p.save()

    # else:

    #     # Obtener datos de la empresa
    #     nombre_empresa = config.nombre
    #     direccion_empresa = config.direccion
    #     telefono_empresa = config.telefono
    #     email_empresa = str(config.redes)
        
    #     #Crear el objeto
    #     response = HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition'] = f'attachment; filename="presupuesto_{venta.id}.pdf"'

    #     # Crear el lienzo PDF
    #     p = canvas.Canvas(response, pagesize=legal)

    #     # Agregar contenido al lienzo
    #     y = 950  # Posición vertical inicial
    #     x = 50
    #     # Color de fondo del reporte
    #     color_1=220/256 # <-- por definicion tengo que poner el valor rgb en %, es decir valor_rgb/256
    #     color_2=220/256
    #     color_3=220/256
    #     p.setFillColorRGB(color_1, color_2, color_3)
    #     p.rect(0, 0, 2000, 2000, fill=True)

    #     # RECTANGULO SIPERIOR
    #     p.setFillColorRGB(200, 200, 200)  # Color de fondo gris claro
    #     p.setStrokeColorRGB(255, 255, 255)  # Color del borde blanco
    #     p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    #     p.rect(30, 870, 360, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco
    #     p.rect(400, 870, 180, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    #     if config.imagen:
    #         logo_path = config.imagen.path
    #     else:
    #         logo_path = os.path.join(current_directory, 'logo.png')
            
    #     # Verificar si el archivo de imagen del logo existe
    #     if logo_path:
    #         # Tamaño y posición del logo
    #         logo_width = 100  # Ancho del logo
    #         logo_height = 100 # Alto del logo
    #         logo_x = 440  # Posición horizontal del logo
    #         logo_y = 875  # Posición vertical del logo

    #         # Agregar el logo al lienzo PDF
    #         logo_image = ImageReader(logo_path)
    #         p.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)
        

    #     # RECTANGULO SIPERIOR
    #     p.setStrokeColorRGB(255, 255, 255)  # Color del borde blanco
    #     p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    #     p.rect(30, 750, 550, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    #     # Escribir el nombre de la empresa encima del fondo gris
    #     p.setFillColorRGB(0, 0, 0) 
    #     p.setFont("Helvetica-Bold", 18)  
    #     p.drawString(x, y, nombre_empresa)
    #     y -= 25

    #     p.setFont("Helvetica", 12)  # Fuente normal
    #     p.drawString(x, y, direccion_empresa)
    #     y -= 18
    #     p.drawString(x, y, telefono_empresa)
    #     y -= 18
    #     p.drawString(x, y, email_empresa)
    #     y -= 18

    #     if True:

    #         # Seccion de la izquierda (datos de la venta) --------->
    #         y = 841
            
    #         p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #         p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
    #         p.drawString(x - 10, y, f"DATOS DE LA VENTA")
    #         y -= 20

    #         p.setFillColorRGB(0, 0, 0)
    #         p.setFont("Helvetica-Bold", 10)
    #         p.drawString(x, y, "Numero venta: ")
    #         p.setFont("Helvetica", 10)
    #         codigo_str = str(venta.id)
    #         p.drawString(122, y, codigo_str.zfill(4))
    #         y -= 20

    #         p.setFont("Helvetica-Bold", 10)
    #         p.drawString(x, y, "Fecha: ")
    #         p.setFont("Helvetica", 10)  # Fuente normal
    #         fecha = venta.FECHA.strftime("%H:%M %d/%m/%Y")
    #         p.drawString(90, y, fecha)
    #         y -= 20


    #         # Seccion de la derecha (datos del cliente) --------->
    #         y = 841

    #         p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #         p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
    #         p.drawString(x + 220, y, f"DATOS DEL CLIENTE")
    #         p.setFillColorRGB(0, 0, 0)
    #         y -= 20

    #         if venta.CLIENTE:

    #             p.setFont("Helvetica-Bold", 10)
    #             p.drawString(x + 250, y, "Cliente:")
    #             p.setFont("Helvetica", 10)  # Fuente normal
    #             p.drawString(x + 310, y, f'{venta.CLIENTE}')
    #             y -= 15

    #             p.setFont("Helvetica-Bold", 10)
    #             p.drawString(x + 250, y, "Direccion:")
    #             p.setFont("Helvetica", 10)  # Fuente normal
    #             p.drawString(x + 310, y, f'{venta.CLIENTE.DIRECCION}')
    #             y -= 15

    #             p.setFont("Helvetica-Bold", 10)
    #             p.drawString(x + 250, y, "Telefono:")
    #             p.setFont("Helvetica", 10)  # Fuente normal
    #             p.drawString(x + 310, y, f'{venta.CLIENTE.TELEFONO}')


    #         else:
    #             p.setFont("Helvetica-Bold", 10)
    #             p.drawString(x + 250, y, "Cliente:")
    #             p.setFont("Helvetica", 10)  # Fuente normal
    #             p.drawString(90, x + 310, f'Consumidor Final')
    #             y -= 15

    #     y -= 35

    #     # Obtener los gastos
    #     productos = ingredientereceta.objects.filter(receta=venta)

    #     p.setFillColorRGB(1,1,1)
    #     p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    #     p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    #     p.rect(30, 240, 550, 500, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    #     p.setFillColorRGB(1,1,1)
    #     p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    #     p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    #     p.rect(30, 140, 550, 90, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco
        
    #     p.setFillColorRGB(1,1,1)
    #     p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    #     p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    #     p.rect(30, 20, 550, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco
        
    #     y -= 20

    #     if productos:
    #         p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #         p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
    #         p.drawString(x - 10, y - 5, f"PRODUCTOS INCLUIDOS EN EL PRESUPUESTO ({productos.count():,.2f})")
    #         y -= 20

    #         p.setFillColorRGB(0, 0, 0)
    #         p.setFont("Helvetica-Bold", 10)
    #         p.drawString(x, y, "NOMBRE DE PRODUCTO")
    #         p.drawString(x + 230, y, "CANTIDAD")
    #         p.drawString(x + 330, y, "P. UNITARIO")
    #         p.drawString(x + 450, y, "SUBTOTAL")
    #         y -=20

    #         numero_item  = 1
    #         for producto in productos:

    #             p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #             p.setFont("Helvetica-Bold", 10)
    #             p.drawString(x - 16, y, f"{numero_item}")
    #             p.setFillColorRGB(0, 0, 0)
    #             p.setFont("Helvetica", 10)

    #             nombre_producto = f"{producto.producto.PRODUCTO}"
    #             p.drawString(x, y, f"{nombre_producto}")
    #             p.drawString(x + 245, y, f"{producto.cantidad} {producto.producto.UNIDAD_MEDIDA[:3]}")
    #             precio=float(producto.precio_unitario)
    #             precio_total=float(precio) * float(producto.cantidad)
    #             p.drawString(x + 340, y, f"{config.moneda} {precio:,.2f}")
    #             p.drawString(x + 440, y, f"{config.moneda} {precio_total:,.2f}")

    #             numero_item += 1
    #             y -= 15
    #         y -= 10
    #     insumos_compuestos = insumoCompuestoReceta.objects.filter(pedido=venta)
        
    #     if insumos_compuestos:
    #         p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #         p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
    #         p.drawString(x - 10, y - 5, f"PRODUCTOS COMPUESTOS INCLUIDOS EN EL PRESUPUESTO ({insumos_compuestos.count():,.2f})")
    #         y -= 30

    #         p.setFillColorRGB(0, 0, 0)
    #         p.setFont("Helvetica-Bold", 10)
    #         p.drawString(x, y, "NOMBRE DE PRODUCTO")
    #         p.drawString(x + 230, y, "CANTIDAD")
    #         p.drawString(x + 330, y, "P. UNITARIO")
    #         p.drawString(x + 450, y, "SUBTOTAL")
    #         y -=20

    #         numero_item  = 1
    #         total=0
    #         for producto in insumos_compuestos:

    #             p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #             p.setFont("Helvetica-Bold", 10)
    #             p.drawString(x - 16, y, f"{numero_item}")
    #             p.setFillColorRGB(0, 0, 0)
    #             p.setFont("Helvetica", 10)

    #             nombre_producto = f"{producto.insumo_Compuesto}"
    #             p.drawString(x, y, f"{nombre_producto}")
    #             p.drawString(x + 245, y, f"{producto.cantidad} Uni")
    #             precio=float(producto.insumo_Compuesto.precio_unitario())
    #             precio_total=float(producto.insumo_Compuesto.precio_unitario()) * float(producto.cantidad)
    #             p.drawString(x + 340, y, f"{config.moneda} {precio:,.2f}")
    #             p.drawString(x + 440, y, f"{config.moneda} {precio_total:,.2f}")
    #             total+=precio_total
    #             numero_item += 1
    #             y -=  15



    #     y = 220
    #     comentarios=ComentarioVenta.objects.filter(VENTA=venta)
    #     if comentarios:

    #         # Bloque entrega
    #         p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #         p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
    #         p.drawString(x + 240, y - 5, f"COMENTARIOS")
    #         y -= 20

    #         for comentario in comentarios:
    #             p.setFillColorRGB(1, 0, 0)
    #             p.setFont("Helvetica", 10)
    #             fecha_comentario = comentario.FECHA.strftime("%Y-%m-%d")# %H:%M
    #             p.drawString(x + 250, y, fecha_comentario)
    #             p.setFillColorRGB(0, 0, 0)
    #             p.drawString(x + 315, y, comentario.COMENTARIO )
    #             y -= 10

    #     y = 120
    #     medios_de_pago_select = PagosPedidos.objects.filter(PEDIDO=venta)
       
    #     pagos=0
    #     if medios_de_pago_select:
    #         # Bloque entrega
    #         p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #         p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
    #         p.drawString(x - 10, y - 5, f"PAGOS DEL CLIENTE")
    #         y -= 20

    #         p.setFillColorRGB(0, 0, 0)
    #         p.setFont("Helvetica-Bold", 10)
    #         p.drawString(x, y, "MEDIO DE PAGO")
    #         p.drawString(x + 150, y, "TOTAL")

    #         y -=20

    #         numero_item  = 1

    #         for pago in medios_de_pago_select:
                
    #             p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
    #             p.setFont("Helvetica-Bold", 10)
    #             p.drawString(x - 16, y, f"{numero_item}")
            
    #             p.setFillColorRGB(0, 0, 0)
    #             p.setFont("Helvetica", 10)
    #             p.drawString(x, y, f"{pago.MEDIO_DE_PAGO}")
    #             p.drawString(x + 150, y, f"{config.moneda} {(pago.TOTAL):,.2f}")

    #             if pago.MEDIO_DE_PAGO.Nombre != "Cuenta Corriente":
    #                 pagos += pago.TOTAL
                        
    #             numero_item += 1
    #             y -=  10

    #     y = 110
    #     p.setFillColorRGB(0, 0, 0)
    #     p.setFont("Helvetica-Bold", 13)
    #     p.drawString(320, y, "Total Presupuestado: ")
    #     p.setFillColorRGB(1, 0, 0)
    #     p.setFont("Helvetica", 13)  # Fuente normal
    #     p.drawString(465, y, f"{config.moneda} {total:,.2f}")

    #     y -= 20

    #     p.setFillColorRGB(0, 0, 0)
    #     p.setFont("Helvetica-Bold", 13)
    #     p.drawString(320, y, "Descuentos: ")
    #     p.setFillColorRGB(1, 0, 0)
    #     p.setFont("Helvetica", 13)  # Fuente normal
    #     p.drawString(465, y, f"{config.moneda} {0:,.2f}")

    #     y -= 20

    #     p.setFillColorRGB(0, 0, 0)
    #     p.setFont("Helvetica-Bold", 13)
    #     p.drawString(320, y, "Suma de Pagos: ")
    #     p.setFillColorRGB(1, 0, 0)
    #     p.setFont("Helvetica", 13)  # Fuente normal
    #     p.drawString(465, y, f"{config.moneda} {pagos:,.2f}")

    #     y -= 30

    #     p.setFillColorRGB(0, 0, 0)
    #     p.setFont("Helvetica-Bold", 16)
    #     p.drawString(320, y, "PENDIENTE: ")
    #     p.setFillColorRGB(1, 0, 0)
    #     p.setFont("Helvetica", 16)
    #     total_bruto = float(total) - float(pagos)
    #     p.drawString(465, y, f"{config.moneda} {total_bruto:,.2f}")

    #     p.save()

    return response
