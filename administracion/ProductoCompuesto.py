from django.http import HttpResponse
from reportlab.lib.pagesizes import legal
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from django.contrib import admin, messages
from administracion.models import ComentarioVenta, Configuracion, InsumoInsumoCompuesto, PagosPedidos, ingredientereceta, insumoCompuestoReceta
import os
from django.db import models

@admin.action(description="Descargar detalle")
def generar_receta(modeladmin, request, queryset):

    if len(queryset) != 1:
        messages.error(request, "Seleccione solo un producto para generar el informe.")
        return

    producto = queryset[0]
    config = Configuracion.objects.first()
    current_directory = os.getcwd()

    nombre_empresa = config.nombre
    direccion_empresa = config.direccion
    telefono_empresa = config.telefono
    email_empresa = str(config.redes)

    numero_item = 1

    #Crear el objeto
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{producto.id}.pdf"'

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
        y = 841
        p.setFillColorRGB(0.6, 0.6, 0.6)  # Color de texto negro
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x - 10, y, f"DETALLE DE PRODUCTO")
        y -= 20
        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Nombre del producto: ")
        p.setFont("Helvetica", 10)
        p.drawString(160, y, str(producto.DESCRIPCION))
        y -= 20
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Categoria:")
        p.setFont("Helvetica", 10)  # Fuente normal
        p.drawString(115, y, f'{producto.CATEGORIA}')
        y -= 20
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Porciones Resultantes:")
        p.setFont("Helvetica", 10)  # Fuente normal
        p.drawString(170, y, f'{producto.UNIDADES_RESULTANTES}')

    y -= 35

    productos = InsumoInsumoCompuesto.objects.filter(insumo_compuesto=producto)

    p.setFillColorRGB(1,1,1)
    p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    p.rect(30, 140, 550, 600, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    p.setFillColorRGB(1,1,1)
    p.setStrokeColorRGB(1, 1, 1)  # Color del borde blanco
    p.setLineWidth(1)  # Grosor del borde (ajusta según sea necesario)
    p.rect(30, 20, 550, 110, fill=True, stroke=True)  # Dibujar un rectángulo detrás del texto con borde blanco

    y -= 20
    if productos:
        p.setFillColorRGB(0.6, 0.6, 0.6)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x - 10, y - 5, f"Insumos contemplados en la composicion: ({productos.count():,.2f})")
        y -= 20

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Detalle de insumo")
        p.drawString(x + 230, y, "Cantdidad")
        p.drawString(x + 330, y, "Precion Unitario")
        p.drawString(x + 450, y, "Subtotal")
        y -=20

        numero_item  = 1
        for insumo in productos:

            p.setFillColorRGB(0.6, 0.6, 0.6)
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x - 16, y, f"{numero_item}")
            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 10)

            # Generar nombre de producto
            nombre_producto = f"{insumo.insumo.PRODUCTO} x {insumo.insumo.CANTIDAD} {insumo.insumo.UNIDAD_MEDIDA[:3]}"
            p.drawString(x, y, f"{nombre_producto}")
            
            # Mostrar la cantidad y la unidad de medida utilizada
            p.drawString(x + 245, y, f"{insumo.cantidad} {insumo.medida_uso}")
            
            # Calcular el precio unitario y el subtotal
            precio_unitario = float(insumo.total()) / float(insumo.cantidad)
            precio_total = float(insumo.total())

            # Mostrar los precios formateados
            p.drawString(x + 340, y, f"{config.moneda} {precio_unitario:,.2f}")
            p.drawString(x + 440, y, f"{config.moneda} {precio_total:,.2f}")


            numero_item += 1
            y -= 15
        y -= 10

    y = 110
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(250, y, "Costo total: ")
    p.setFillColorRGB(1, 0, 0)
    p.setFont("Helvetica", 13)  # Fuente normal
    p.drawString(480, y, f"{config.moneda} {float(producto.costo_total()):,.2f}")

    y -= 20
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(250, y, "Rentabilidad:")
    p.setFillColorRGB(1, 0, 0)
    p.setFont("Helvetica", 13) 
    p.drawString(480, y, f'% {float(producto.RENTABILIDAD):,.2f}')

    y -= 20
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(250, y, "Precio de Venta Unitario: ")
    p.setFillColorRGB(1, 0, 0)
    p.setFont("Helvetica", 13)  # Fuente normal
    p.drawString(480, y, f"{config.moneda} {float(producto.precio_unitario()):,.2f}")

    y -= 30
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 15)
    p.drawString(250, y, "Precio de Venta Total: ")
    p.setFillColorRGB(1, 0, 0)
    p.setFont("Helvetica", 15)  # Fuente normal
    p.drawString(480, y, f"{config.moneda} {float(producto.precio_total()):,.2f}")
    y -= 30

    p.save()

    return response
