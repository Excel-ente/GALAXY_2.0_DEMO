from django import forms
from django.db import models
from django.contrib import admin
from datetime import date
from django.contrib import messages
from administracion.ProductoCompuesto import generar_receta
from administracion.forms import ConfiguracionForm
from .models import *
from .Funciones import Entregar,Aceptar,ConfirmarCompra
from import_export.admin import ImportExportModelAdmin
import pytz
from .presupuesto import generar_presupuesto
from django.utils.formats import date_format
from django.utils import timezone
from django.db.models import Sum
from django.utils.html import format_html
from django.shortcuts import redirect
from django.db.models import F, Sum, ExpressionWrapper, DecimalField

admin.site.site_header = "GALAXY 2.0"
admin.site.site_title = "GALAXY 2.0"

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    fields = ('PRODUCTO', 'CANTIDAD','PRECIO','DESCUENTO','ActualizarCosto')
    autocomplete_fields = ('PRODUCTO',)

class ComentarioVentaInline(admin.TabularInline):
    model = ComentarioVenta
    extra = 0
    fields = ('COMENTARIO',)
    readonly_fields = ('FECHA',)
    
class PagosComprasInline(admin.TabularInline):
    model = PagosCompras
    extra = 1
    fields = ('MEDIO_DE_PAGO', 'TOTAL',)

class PagosPedidosInline(admin.TabularInline):
    model = PagosPedidos
    extra = 1
    fields = ('MEDIO_DE_PAGO', 'TOTAL',)

class IngredientePedidoInline(admin.TabularInline):
    model = ingredientereceta
    extra = 1
    fields = ('producto', 'cantidad', 'PRECIO_UNITARIO', 'medida_uso','descuento','SUBTOTAL')
    readonly_fields = ('PRECIO_UNITARIO', 'medida_uso', 'SUBTOTAL',)
    autocomplete_fields = ('producto',)

    def PRECIO_UNITARIO(self,obj):
        config = Configuracion.objects.first()
        if obj.receta.ESTADO == 'Pendiente':
            formateo = str(config.moneda) + " {:,.2f}".format(obj.producto.precio_venta() or 0) 
        else:
            formateo = str(config.moneda) + " {:,.2f}".format(obj.precio_unitario or 0)
        return formateo

    def SUBTOTAL(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.subtotal)
        return formateo

class insumoCompuestoRecetaInline(admin.TabularInline):
    model = insumoCompuestoReceta
    extra = 1
    fields = ('insumo_Compuesto', 'cantidad','PRECIO_UNITARIO','SUBTOTAL')
    readonly_fields =('PRECIO_UNITARIO','SUBTOTAL',)
    autocomplete_fields = ('insumo_Compuesto',)


    def PRECIO_UNITARIO(self,obj):
        config = Configuracion.objects.first()
        if obj.pedido.ESTADO == "Pendiente":
            formateo = str(config.moneda) + " {:,.2f}".format(float(obj.insumo_Compuesto.precio_unitario()) or 0)
        else:
            formateo = str(config.moneda) + " {:,.2f}".format(obj.precio() or 0)
        return formateo
 
    def SUBTOTAL(self,obj):
        config = Configuracion.objects.first()
        if obj.pedido.ESTADO == "Pendiente":
            formateo = str(config.moneda) + " {:,.2f}".format(float(obj.insumo_Compuesto.precio_unitario()) * float(obj.cantidad) or 0)
        else:
            formateo = str(config.moneda) + " {:,.2f}".format(float(obj.total()) or 0) 
        return formateo

class InsumoInline(admin.TabularInline):
    model = InsumoInsumoCompuesto
    extra = 1
    fields = ('insumo', 'cantidad', 'medida_uso', 'precio_unit', 'total',)
    readonly_fields = ('precio_unit', 'total',)
    autocomplete_fields = ('insumo',)
    fk_name = 'insumo_compuesto'

    def precio_unit(self, obj):
        config = Configuracion.objects.first()
        precio_unitario = obj.insumo.precio_venta() if obj.insumo else 0
        return f'{config.moneda} {precio_unitario:,.2f}'
    
    def total(self, obj):
        config = Configuracion.objects.first()
        precio_unitario = obj.insumo.precio_venta() if obj.insumo else 0
        total = obj.total()
        return f'{config.moneda} {total:,.2f}'

class InsumoCompuestoDetalleInline(admin.TabularInline):
    model = InsumoCompuestoDetalle
    fk_name = 'insumo_compuesto_principal'  # Especifica la clave foránea
    extra = 1
    fields = ('insumo_compuesto_referencia','cantidad','subtotal')
    readonly_fields = ('subtotal',)
    autocomplete_fields = ('insumo_compuesto_referencia',)

    def subtotal(self,obj):
        signo = Configuracion.objects.first().moneda    
        total = float(obj.insumo_compuesto_referencia.precio_unitario()) * float(obj.cantidad)
        return f'{signo} {total:,.2f}'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "insumo_compuesto_referencia":
            # Obtén el ID del insumo compuesto principal del request
            try:
                obj_id = request.resolver_match.kwargs.get('object_id')
                if obj_id:
                    kwargs["queryset"] = InsumoCompuesto.objects.exclude(pk=obj_id)
            except Exception as e:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    list_display = ('NOMBRE_Y_APELLIDO','DIRECCION','TELEFONO','estado_de_cuenta')
    search_fields = ('NOMBRE_Y_APELLIDO',)

    def estado_de_cuenta(self,obj):
        config = Configuracion.objects.first()
        if obj.NOMBRE_Y_APELLIDO == "Consumidor Final":
            formateo = "No aplica"
        else:
            formateo = str(config.moneda) + " {:,.2f}".format(obj.Cuenta_Corriente())
        return formateo

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(NOMBRE_Y_APELLIDO='Consumidor Final')

@admin.register(Categoria)
class CategoriaAdmin(ImportExportModelAdmin):
    list_display = ('DESCRIPCION',)
    list_filter = ('DESCRIPCION',)

@admin.register(Proveedor)
class ProveedorAdmin(ImportExportModelAdmin):
    list_display = ('EMPRESA', 'NOMBRE','DIRECCION', 'EMAIL','TELEFONO','estado_de_cuenta')
    ordering = ('EMPRESA',)
    search_fields = ('EMPRESA', 'NOMBRE',)

    def estado_de_cuenta(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.cuenta_corriente)
        return formateo
    
@admin.register(Gastos)
class GastosAdmin(ImportExportModelAdmin):
    list_display = ('FECHA','DETALLE', 'IMPORTE',)
    ordering = ('DETALLE',)

    def IMPORTE(self, obj):
        config = Configuracion.objects.first()
        return str(config.moneda) + " {:,.2f}".format(obj.TOTAL)

@admin.register(Insumo)
class InsumoAdmin(ImportExportModelAdmin):
    list_display = ('ESTADO','Producto','PROVEEDOR', 'Costo_Unitario','Precio_venta','en_inventario','UNIDAD_MEDIDA','Rentabilidad')
    ordering = ('PRODUCTO',)
    list_filter =('PRODUCTO','PROVEEDOR')
    exclude=('COSTO_UNITARIO','STOCK','RENTABILIDAD')#'PRECIO_VENTA',
    readonly_fields = ('Precio_venta','Costo_Unitario',)
    search_fields = ('PRODUCTO',)
    list_per_page = 25
    list_display_links = ('Producto',)

    def ESTADO(self, obj):
        estado = obj.HABILITAR_VENTA
        if estado:
            return f'🟢 Publicado'
        else:
            return f'🔴 No Publicado'
        
    def Rentabilidad(self, obj):
        rentabilidad = obj.rentabilidad() or 0
        if rentabilidad > 0:
            return f'🔼 % {rentabilidad:.2f}'
        else:
            return f'🔻% {rentabilidad:.2f}'

    def Producto(self, obj):
        stock = f'{obj.PRODUCTO} x{obj.UNIDAD_MEDIDA[:3]}'
        return stock 

    def Costo_Unitario(self, obj):
        config = Configuracion.objects.first()
        costo_unitario = float(obj.costo_unitario())
        return f'{config.moneda} {costo_unitario:,.2f}'

    def Precio_venta(self, obj):
        config = Configuracion.objects.first()
        precio = float(obj.precio_venta())
        return f'{config.moneda} {precio:,.2f}'
    
    def en_inventario(self, obj):
        if Configuracion.objects.first().mostrar_stock_pendiente:     
            stock = f'{obj.stock_actual():,.3f} <b style="color: red;">{obj.stock_comprometido():,.2f}</b>'
            return format_html(stock)   
        else:
            stock = f'{obj.stock_actual():,.3f}'
            return stock

@admin.register(InsumoCompuesto)
class InsumoCompuestoAdmin(ImportExportModelAdmin):
    list_display = ('ESTADO', 'DESCRIPCION', 'UNIDADES', 'COSTO_UNITARIO', 'COSTO_TOTAL', 'Rentabilidad', 'PRECIO_UNITARIO', 'PRECIO_TOTAL', 'stock_actual')
    list_filter = ('HABILITAR_VENTA',)
    exclude = ('RENTABILIDAD',)
    readonly_fields = ('COSTO_UNITARIO', 'COSTO_TOTAL', 'PRECIO_UNITARIO', 'PRECIO_TOTAL')
    search_fields = ['DESCRIPCION',]
    inlines = [InsumoCompuestoDetalleInline, InsumoInline]
    actions = [generar_receta,]
    
    def UNIDADES(self, obj):
        return obj.UNIDADES_RESULTANTES

    def ESTADO(self, obj):
        estado = obj.HABILITAR_VENTA
        if estado:
            return f'🟢 Publicado'
        else:
            return f'🔴 No Publicado'
        
    def Rentabilidad(self, obj):
        rentabilidad = float(obj.rentabilidad())
        if rentabilidad > 0:
            return f'🔼 % {rentabilidad:.2f}'
        else:
            return f'🔻% {rentabilidad:.2f}'
        
    def COSTO_UNITARIO(self, obj):
        config = Configuracion.objects.first()
        costo = float(obj.costo_unitario())
        return f'{config.moneda} {costo:,.2f}'

    def COSTO_TOTAL(self, obj):
        config = Configuracion.objects.first()
        costo = float(obj.costo_total())
        return f'{config.moneda} {costo:,.2f}'

    def PRECIO_UNITARIO(self, obj):
        config = Configuracion.objects.first()
        costo = float(obj.precio_unitario())
        formateo = str(config.moneda) + " {:,.2f}".format(costo)
        return formateo
    
    def PRECIO_TOTAL(self, obj):
        config = Configuracion.objects.first()
        costo = float(obj.precio_total())
        formateo = str(config.moneda) + " {:,.2f}".format(costo)
        return formateo

    def stock_actual(self, obj):
        return obj.stock_str()
 
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = [
        PagosPedidosInline,
        IngredientePedidoInline,
        insumoCompuestoRecetaInline,
        ComentarioVentaInline,
    ]
    list_display = ('Presupuesto','Estado','CLIENTE','Total_pedido','Total_pagos','Fecha_de_entrega',)
    list_filter = ('CLIENTE','ESTADO')
    search_fields = ('CLIENTE__NOMBRE_Y_APELLIDO',)
    readonly_fields = ('Total_pedido',)
    autocomplete_fields = ('CLIENTE',)
    list_per_page = 25
    list_display_links = ('Presupuesto',)
    actions = [Aceptar, Entregar,generar_presupuesto]
    exclude=('VALIDO_HASTA','COSTO_RECETA','COSTO_DIARIO','MANO_DE_OBRA','ARTICULO','ADICIONALES','COSTO_FINAL','GASTOS_ADICIONALES','ESTADO')
    #'FECHA',
    formfield_overrides = {
        models.DecimalField: {'widget': forms.TextInput},
    }

    def Presupuesto(self,obj):
        presup = obj.pk
        return f'# {presup}'

    def Total_pedido(self, obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.precio_total())
        return formateo

    def Total_pagos(self, obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.Total_Pagos)
        return formateo

    def Ultima_Actualizacion(self, obj): 
        hora_buenos_aires = pytz.timezone('America/Argentina/Buenos_aires')
        fecha_hora = obj.ULTIMA_ACTUALIZACION.astimezone(hora_buenos_aires)
        formateo = fecha_hora.strftime("%H:%M %d/%m/%Y")

        formateo = "📆 " +formateo
        return formateo

    def Estado(self,obj):
        if obj.ESTADO=="Pendiente":
            return "🔴 Pendiente"
        elif obj.ESTADO=="Aceptado":
            return "🟢 Aceptado"
        else:
            return "🔵 Entregado"

    def costo(self,obj):
        costo=obj.costo_pedido()
        return costo
    
    def Fecha_de_entrega(self, obj):
        formateo = "📆 " + str(obj.FECHA_ENTREGA)
        return formateo
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request) 
        if request.GET.get('ESTADO__exact') == 'Entregado':
            return queryset  # No aplicar ningún filtro si el filtro 'entregado' está activo
        else:
            return queryset.exclude(ESTADO='Entregado')


    def has_delete_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente



@admin.register(Compras)
class ComprasAdmin(ImportExportModelAdmin):
    list_display = ('FECHA','PROVEEDOR','TOTAL_COMPRA','TOTAL_PAGOS','estado',)
    list_filter = ('PROVEEDOR','ESTADO')
    exclude=('ESTADO',)
    readonly_fields=('TOTAL_COMPRA','ESTADO',)
    autocomplete_fields = ('PROVEEDOR',)
    search_fields = ('PROVEEDOR',)
    actions = [ConfirmarCompra,]
    inlines = [
        PagosComprasInline,
        DetalleCompraInline,
    ]

    def estado(self,obj):
        if obj.ESTADO:
            return "🟢 Confirmada"
        else:
            return "🔴 Pendiente"

    def TOTAL_COMPRA(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.Total)
        return formateo
    
    def TOTAL_PAGOS(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.Total_Pagos)
        return formateo
    
@admin.register(DetalleCompra)
class DetalleCompraAdmin(ImportExportModelAdmin):
    list_display = ('FECHA','PROVEEDOR','PRODUCTO','CANTIDAD','precio_unitario','DESCUENTO','NETO_UNOTARIO','TOTAL')
    list_filter = ('COMPRA','COMPRA__PROVEEDOR','PRODUCTO')

    def TOTAL(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.Total)
        return formateo

    def precio_unitario(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.PRECIO)
        return formateo

    def NETO_UNOTARIO(self,obj):
        config = Configuracion.objects.first()
        precio = obj.PRECIO
        descuento = obj.DESCUENTO
        precio_neto = precio - (precio * descuento / 100)
        formateo = str(config.moneda) + " {:,.2f}".format(precio_neto)
        return formateo
    
    def PROVEEDOR(self,obj):
        if obj.COMPRA.PROVEEDOR:
            texto = obj.COMPRA.PROVEEDOR
            return texto
        else:
            "Sin Proveedor asignado"
    
@admin.register(ingredientereceta)
class ingredienterecetaAdmin(ImportExportModelAdmin):
    list_display = ('FECHA','cliente_','producto','cantidad','medida_uso','PRECIO_UNITARIO','TOTAL',)
    list_filter = ('producto','receta__CLIENTE')
    autocomplete_fields = ('producto',)

    def FECHA(self,obj):
        fecha  = obj.receta.ULTIMA_ACTUALIZACION
        return fecha

    def TOTAL(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.subtotal)
        return formateo
    
    def PRECIO_UNITARIO(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.subtotal)
        return formateo

    def cliente_(self,obj):
        if obj.receta.CLIENTE:
            texto = obj.receta.CLIENTE
            return texto
        else:
            "Sin Cliente asignado"

@admin.register(Fabrica)
class FabricaAdmin(admin.ModelAdmin):
    list_display = ('Estado', 'FECHA', 'RECETA', 'UNIDADES_RESULTANTES', 'VALIDO_HASTA')
    ordering = ('RECETA',)
    list_filter = ('RECETA',)
    search_fields = ('RECETA',)
    exclude = ('ESTADO',)
    list_per_page = 20
    list_display_links = ('Estado', 'FECHA', 'RECETA', 'UNIDADES_RESULTANTES', 'VALIDO_HASTA')
    actions = ['verificar_insumos', 'realizar_fabricacion']

    def Estado(self,obj):
        if obj.ESTADO=="Pendiente":
            return "🔴 Pendiente"
        elif obj.ESTADO=="En proceso":
            return "🟢 En proceso"
        else:
            return "🔵 Finalizado"
        
    def verificar_insumos(self, request, queryset):
        for fabrica in queryset:
            estado, insumos_faltantes = fabrica.control_insumos()
            if estado:
                if fabrica.ESTADO == "Finalizado":
                    self.message_user(request, f'La fabricación #{fabrica.pk} ya se encuentra realizada.', level=messages.ERROR)
                else:
                    self.message_user(request, f'La fabricación #{fabrica.pk} tiene todos los insumos necesarios.', level=messages.SUCCESS)
            else:
                insumos_faltantes_str = ', '.join([f"{insumo['insumo']} (Faltan: {float(insumo['cantidad_necesaria']) - float(insumo['cantidad_disponible'])} {insumo['insumo'].UNIDAD_MEDIDA})" for insumo in insumos_faltantes])
                self.message_user(request, f'La fabricación #{fabrica.pk} no tiene suficientes insumos. Faltantes: {insumos_faltantes_str}', level=messages.ERROR)

    verificar_insumos.short_description = "Verificar insumos necesarios"

    def realizar_fabricacion(self, request, queryset):
        for fabrica in queryset:
            estado, resultado = fabrica.realizar_fabricacion()
            if estado:
                if fabrica.ESTADO == "Finalizado":
                    self.message_user(request, f'La fabricación #{fabrica.pk} ya se encuentra realizada.', level=messages.ERROR)
                else:
                    self.message_user(request, resultado, level=messages.SUCCESS)
            else:
                insumos_faltantes_str = ', '.join([f"{insumo['insumo']} (Faltan: {float(insumo['cantidad_necesaria']) - float(insumo['cantidad_disponible'])} {insumo['insumo'].UNIDAD_MEDIDA})" for insumo in resultado])
                self.message_user(request, f'La fabricación #{fabrica.pk} no se pudo realizar. Faltantes: {insumos_faltantes_str}', level=messages.ERROR)

    realizar_fabricacion.short_description = "Realizar fabricación"

@admin.register(medioDePago)
class medioDePagoAdmin(ImportExportModelAdmin):
    list_display = ('Nombre',)

@admin.register(ComentarioVenta)
class ComentarioVentaAdmin(ImportExportModelAdmin):
    list_display = ('VENTA','COMENTARIO',)
    list_filter = ('VENTA','VENTA__CLIENTE',)

@admin.register(Configuracion)
class ConfiguracionAdmin(ImportExportModelAdmin):
    list_display = ('nombre','direccion','telefono',)
    exclude = ('mostrar_foto',)

@admin.register(PagosPedidos)
class PagosPedidosAdmin(ImportExportModelAdmin):
    list_display = ('CLIENTE','Pedido','MEDIO_DE_PAGO','Importe')
    list_filter = ('MEDIO_DE_PAGO','CLIENTE','PEDIDO__CLIENTE')
    exclude = ('PEDIDO','FECHA')
    autocomplete_fields = ('CLIENTE',)

    def Pedido(self,obj):
        if obj.PEDIDO:
            return obj.PEDIDO
        else:
            texto = "Pago Manual"
            return texto
        
    def Importe(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.TOTAL)
        return formateo

@admin.register(PagosCompras)
class PagosComprasAdmin(ImportExportModelAdmin):
    list_display = ('PROVEEDOR','Compra','MEDIO_DE_PAGO','Importe')
    list_filter = ('COMPRA__id','PROVEEDOR','COMPRA__PROVEEDOR','MEDIO_DE_PAGO')
    exclude =('COMPRA',)
    search_fields = ('PROVEEDOR',)
    autocomplete_fields = ('PROVEEDOR',)

        
    def Compra(self,obj):
        if obj.COMPRA:
            return obj.COMPRA
        else:
            texto = "Pago Manual"
            return texto
        
    def Importe(self,obj):
        config = Configuracion.objects.first()
        formateo = str(config.moneda) + " {:,.2f}".format(obj.TOTAL)
        return formateo
    

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    change_list_template = 'home_custom.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        if request.method == 'POST':
            form = ConfiguracionForm(request.POST, request.FILES)
            if form.is_valid():
                configuracion = form.save(commit=False)
                configuracion.id = 1
                configuracion.save()
                return redirect('.')
        else:
            form = ConfiguracionForm()

        configuracion = Configuracion.objects.first()
        fecha_hoy = timezone.now().date()
        ventas_mes = Pedido.objects.all()
        fecha_desde = date.today()

        mes_ant = fecha_hoy.month - 1
        anio_ant = fecha_hoy.year

        if fecha_hoy.month == 1:
            anio_ant = anio_ant - 1
            mes_ant = 12

        mes_actual = date_format(fecha_desde, 'F')
        ventas_mes_actual = 0
        ventas_mes_anterior = 0 
        compras_mes_actual = 0
        compras_mes_anterior = 0
        gastos_mes_actual = 0
        gastos_mes_anterior = 0


        ventas = Pedido.objects.filter(FECHA__month=fecha_hoy.month,FECHA__year=fecha_hoy.year)
        for venta in ventas:
            if venta.ESTADO != 'Pendiente':
                ventas_mes_actual += venta.precio_total()

        ventas = Pedido.objects.filter(FECHA__month=mes_ant,FECHA__year=anio_ant)
        for venta in ventas:
            if venta.ESTADO != 'Pendiente':
                ventas_mes_anterior += venta.precio_total()

        compras = Compras.objects.filter(FECHA__month=fecha_hoy.month,FECHA__year=fecha_hoy.year)
        for compra in compras:
            if compra.ESTADO == True:
                compras_mes_actual += compra.Total

        compras = Compras.objects.filter(FECHA__month=mes_ant,FECHA__year=anio_ant)
        for compra in compras:
            if compra.ESTADO == True:
                compras_mes_anterior += compra.Total

        gastos = Gastos.objects.filter(FECHA__month=fecha_hoy.month,FECHA__year=fecha_hoy.year)
        for gasto in gastos:
            gastos_mes_actual += gasto.TOTAL


        gastos = Gastos.objects.filter(FECHA__month=mes_ant,FECHA__year=anio_ant)
        for gasto in gastos:
            gastos_mes_anterior += gasto.TOTAL

        valuacion_inventario = 0
        productos = Insumo.objects.all()
        for producto in productos:
            cantidad = producto.stock_actual() or 0
            if cantidad > 0:
                valuacion_inventario += float(producto.costo_unitario()) * float(cantidad)

        valuacion_inventario_compuesto = 0
        productos = InsumoCompuesto.objects.all()
        for producto in productos:
            cantidad = producto.stock_actual() or 0
            if cantidad > 0:
                valuacion_inventario_compuesto += float(producto.costo_unitario()) * float(cantidad)

        cuenta_corriente_clientes = 0
        clientes = Cliente.objects.all()
        for cliente in clientes:
            if cliente.Cuenta_Corriente() > 0 and cliente.NOMBRE_Y_APELLIDO != "Consumidor Final":
                cuenta_corriente_clientes += cliente.Cuenta_Corriente()

        cuenta_corriente_proveedores = 0
        proveedores = Proveedor.objects.all()
        for proveedor in proveedores:
            if proveedor.cuenta_corriente > 0:
                cuenta_corriente_proveedores += proveedor.cuenta_corriente

        # Obtener ventas diarias y ganancias diarias
        venta_dash = Pedido.ventas_ultimos()
        venta_dash_total = sum(total_venta for _, total_venta, _ in venta_dash)
        ganancias_dash_total = sum(total_ganancia for _, _, total_ganancia in venta_dash)

        # Filtrar ingredientereceta por los pedidos de este mes
        ventas_producto_mes = ingredientereceta.objects.filter(
            receta__FECHA__year=fecha_hoy.year,
            receta__FECHA__month=fecha_hoy.month
        ).values(
            'producto__PRODUCTO',
            'producto__UNIDAD_MEDIDA',
            'subtotal'
        ).annotate(
            total_vendido=Sum('cantidad'),
            ganancias=Sum(
                ExpressionWrapper(
                    (F('precio_unitario') - F('costo_unitario')) * F('cantidad'),
                    output_field=DecimalField(max_digits=20, decimal_places=2)
                )
            )
        ).order_by('-total_vendido')[:15]

        if Configuracion.objects.filter(id=1).exists():
            extra_context['inicial'] = True
        else:
            extra_context['inicial'] = False

        extra_context['configuracion'] = configuracion
        extra_context['mes_actual'] = mes_actual
        extra_context['ventas_mes_actual'] = round(ventas_mes_actual, 2)
        extra_context['compras_mes_actual'] = round(compras_mes_actual, 2)
        extra_context['ventas_mes_anterior'] = round(ventas_mes_anterior, 2)
        extra_context['compras_mes_anterior'] = round(compras_mes_anterior, 2)
        extra_context['gastos_mes_actual'] = round(gastos_mes_actual, 2)
        extra_context['gastos_mes_anterior'] = round(gastos_mes_anterior, 2)
        extra_context['valuacion_inventario'] = round(valuacion_inventario, 2)
        extra_context['valuacion_inventario_compuesto'] = round(valuacion_inventario_compuesto, 2)
        extra_context['ventas_mes'] = ventas_mes
        extra_context['venta_dash'] = venta_dash
        extra_context['ventas_producto_mes'] = ventas_producto_mes
        extra_context['venta_dash_total'] = venta_dash_total
        extra_context['ganancias_dash_total'] = ganancias_dash_total  # Nueva variable para ganancias totales
        extra_context['cuenta_corriente_clientes'] = cuenta_corriente_clientes
        extra_context['cuenta_corriente_proveedores'] = cuenta_corriente_proveedores

        extra_context['form'] = form

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(MiTienda)
class MiTiendaAdmin(admin.ModelAdmin):
    change_list_template = 'tienda.html'

    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}

        producto_list = Insumo.objects.all()
        producto_compuesto_list = InsumoCompuesto.objects.all()
        configuracion = Configuracion.objects.first()

        extra_context['producto_compuesto_list'] = producto_compuesto_list
        extra_context['producto_list'] = producto_list
        extra_context['configuracion'] = configuracion

        return super().changelist_view(request, extra_context=extra_context)





