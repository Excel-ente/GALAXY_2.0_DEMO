
import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

UnidadDeMedida = [
    ("Unidades","Unidades"),
    ("Kilogramos","Kilogramos"),
    ("Litros","Litros"),
    ("Gramos","Gramos"),
    ("Mililitros","Mililitros"),
    ("Onzas","Onzas"),
    ("Libras","Libras"),
    ("Mts","Mts")
]

Estado = [
    ("Pendiente","Pendiente"),
    ("Aceptado","Aceptado"),
    ("Entregado","Entregado"),
]

Estado_fabrica = [
    ("Pendiente","Pendiente"),
    ("En proceso","En proceso"),
    ("Finalizado","Finalizado"),
]

unit_conversions = {
    'Litros': 1,
    'Mililitros': 1000,
    'Kilogramos': 1,
    'Gramos': 1000,
    'Unidades': 1,
    'Onzas': 1,
    'Libras': 1,
    'Mts': 1
}

def validate_image_size(value):
    width, height = value.width, value.height
    if width != 500 or height != 500:
        raise ValidationError('La imagen debe ser de 500x500 píxeles.')

class Configuracion(models.Model):
    nombre = models.CharField(max_length=255,blank=True,null=True)
    direccion = models.CharField(max_length=255,blank=True,null=True)
    telefono = models.CharField(max_length=255,blank=True,null=True)
    redes = models.CharField(verbose_name="Redes sociales",max_length=255,blank=True,null=True)
    cuit = models.CharField(max_length=255,blank=True,null=True,verbose_name='Nit')
    imagen = models.ImageField(
        upload_to='img/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']), validate_image_size]
    )
    precios_automaticos = models.BooleanField(default=True)
    mostrar_foto = models.BooleanField(default=False)
    mostrar_stock_pendiente = models.BooleanField(default=True)
    fabricar_negativo = models.BooleanField(default=True)
    pisar_costo_inferior = models.BooleanField(default=False)
    moneda = models.CharField(max_length=5,blank=False,null=False,default="$")
    moneda_secundaria = models.CharField(max_length=5,blank=False,null=False,default="$")
    
class medioDePago(models.Model):
    Nombre = models.CharField(max_length=200, null=True, blank=True)

    def clean(self): # Metodo para verificar algun  campo antes de guardar.
        super().clean()

    def __str__(self): # Como se muestra el objeto en una relacion foranea
        return self.Nombre
    
    class Meta: # Metodo para nombrar el modelo
        verbose_name = 'medio de pago'  # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='Medios de pago' # Como se nombra el modelo

class Cliente(models.Model):
    NUMERO_CLIENTE= models.AutoField(primary_key=True)
    NOMBRE_Y_APELLIDO=models.CharField(max_length=120,null=False,blank=False)
    DIRECCION=models.CharField(max_length=255,null=False,blank=False)
    EMAIL=models.CharField(max_length=120,null=True,blank=True)
    TELEFONO =models.CharField(max_length=15,null=False,blank=False)
    HABILITAR_CC = models.BooleanField(default=False)  

    def __str__(self):
        return self.NOMBRE_Y_APELLIDO
    
    def Cuenta_Corriente(self):

        total_deuda=0
        total_pagado=0

        cuenta_corriente = medioDePago.objects.get(Nombre="Cuenta Corriente").pk

        pedidos = PagosPedidos.objects.filter(PEDIDO__CLIENTE=self, MEDIO_DE_PAGO=cuenta_corriente)

        for pedido in pedidos:
            total_deuda += pedido.TOTAL
            
        pagos = PagosPedidos.objects.filter(CLIENTE=self)
        for pago in pagos:
            if pago.PEDIDO:
                pass
            else:
                total_pagado += pago.TOTAL
        
        estado_de_cuenta = total_deuda - total_pagado

        #formateo = "💲{:,.2f}".format(estado_de_cuenta)

        return estado_de_cuenta
    
class Proveedor(models.Model):
    EMPRESA=models.CharField(max_length=120,null=False,blank=False) 
    NOMBRE=models.CharField(max_length=120,null=False,blank=False) 
    DIRECCION=models.CharField(max_length=120,null=True,blank=True)
    EMAIL=models.EmailField(null=True,blank=True)
    TELEFONO=models.CharField(max_length=120,null=False,blank=False)

    def __str__(self):
        return self.EMPRESA
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural ='Proveedores' 

    @property
    def cuenta_corriente(self):

        total_deuda=0
        total_pagado=0

        cuenta_corriente = medioDePago.objects.get(Nombre="Cuenta Corriente").pk

        pedidos = PagosCompras.objects.filter(COMPRA__PROVEEDOR=self,MEDIO_DE_PAGO=cuenta_corriente)
        for pedido in pedidos:
            if pedido.COMPRA.ESTADO:
                total_deuda += pedido.TOTAL
            
        pedidos = PagosCompras.objects.filter(PROVEEDOR=self)
        for pedido in pedidos:
            if pedido.COMPRA:
                pass
            else:
                total_deuda -= pedido.TOTAL
        
        estado_de_cuenta = float(total_deuda - total_pagado)

        return estado_de_cuenta

class Categoria(models.Model):
    DESCRIPCION = models.CharField(max_length=120, null=True, blank=True,unique=True)
    
    def __str__(self):
        return f'{self.DESCRIPCION}'

class Insumo(models.Model):
    CODIGO = models.CharField(max_length=120, null=True, blank=True)
    PRODUCTO = models.CharField(max_length=120, null=False, blank=False,unique=True)
    IMAGEN = models.ImageField(
        upload_to='img/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']), validate_image_size]
    )
    PROVEEDOR=models.ForeignKey(Proveedor,on_delete=models.CASCADE,blank=True,null=True)
    CATEGORIA = models.ForeignKey(Categoria,on_delete=models.CASCADE,null=True, blank=True)
    CANTIDAD = models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    UNIDAD_MEDIDA = models.CharField(max_length=10, choices=UnidadDeMedida, default="Unidades", null=False, blank=False)
    PRECIO_COMPRA = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    RENTABILIDAD = models.DecimalField(max_digits=4, decimal_places=2, default=0, blank=False, null=False)
    PRECIO_VENTA = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)
    HABILITAR_VENTA = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural ='Materiales' 

    def __str__(self):
        return f'{self.PRODUCTO} | x1 {self.UNIDAD_MEDIDA[:3]}  {"$ {:,.2f}".format(self.precio_venta())}'

    def clean(self):
        if self.RENTABILIDAD < 0:
            raise ValidationError("La rentabilidad debe estar comprendida entre el 0% y el 99%")
        
        prd = Insumo.objects.count() or 0
        if prd > 20:
            raise ValidationError("Usted ha llegado al límite de items de la version DEMO.")
    
        super().clean()

    def save(self, *args, **kwargs):
        if not self.CODIGO:
            self.CODIGO = self.pk
        super(Insumo, self).save(*args, **kwargs)

    def ganancias_limpias(self):
        costo = float(self.costo_unitario()) 
        precio_venta = float(self.precio_venta()) 
        dif = float(float(precio_venta) - float(costo))
        return dif
    
    def rentabilidad(self):
        ganancias = self.ganancias_limpias() or 0
        p_venta = self.precio_venta() or 0
        if p_venta > 0:
            rentabilidad = float(ganancias) / float(p_venta) * float(100)
        else:
            rentabilidad = 0
        return rentabilidad
    
    def costo_unitario(self):
        costo = float(self.PRECIO_COMPRA) / float(self.CANTIDAD)
        return costo

    def precio_venta(self):
        costo = 0
        config = Configuracion.objects.first()

        if config.precios_automaticos:
            costo = self.costo_unitario()
            costo = float(float(costo) / float(100 - self.RENTABILIDAD) * 100)
        else:
            costo = float(self.PRECIO_VENTA)
        return costo

    def precio_total(self):

        costo = 0
        config = Configuracion.objects.first()

        if config.precios_automaticos:
            costo = self.costo_unitario()
            costo = float(float(costo) / float(100 - self.RENTABILIDAD) * 100) * float(self.CANTIDAD)
        else:
            costo = self.PRECIO_VENTA  * float(self.CANTIDAD)
           
        return costo

    def stock_actual(self):
        mostrar_pendiente=False
        filtro = "Aceptado"
        config = Configuracion.objects.first()
        if config:
            mostrar_pendiente = config.mostrar_stock_pendiente

        if mostrar_pendiente:
            filtro = "Entregado"
        else:
            filtro = "Aceptado"

        stock = 0
        ventas_productos = ingredientereceta.objects.filter(receta__ESTADO=filtro)
        for producto in ventas_productos:
            if producto.producto.PRODUCTO == self.PRODUCTO:
                stock -= convertir_unidades(producto.cantidad, producto.producto.UNIDAD_MEDIDA, self.UNIDAD_MEDIDA)

        ventas_productos_compuestos = insumoCompuestoReceta.objects.filter(pedido__ESTADO=filtro)
        for venta in ventas_productos_compuestos:
            insumos = InsumoInsumoCompuesto.objects.filter(insumo_compuesto=venta.insumo_Compuesto, insumo=self)
            for insumo in insumos:
                stock -= convertir_unidades(insumo.cantidad * venta.cantidad, insumo.medida_uso, self.UNIDAD_MEDIDA)

        fabricaciones_confirmadas = Fabrica.objects.filter(ESTADO="Finalizado")
        for fabricacion in fabricaciones_confirmadas:
            insumos_fabricacion = InsumoInsumoCompuesto.objects.filter(insumo_compuesto=fabricacion.RECETA)
            for insumo in insumos_fabricacion:
                if insumo.insumo == self:
                    cantidad_a_descontar = convertir_unidades(insumo.cantidad * fabricacion.UNIDADES_RESULTANTES, insumo.medida_uso, self.UNIDAD_MEDIDA)
                    stock -= cantidad_a_descontar 

        compras = DetalleCompra.objects.filter(COMPRA__ESTADO=True)
        for producto in compras:
            if producto.PRODUCTO.PRODUCTO == self.PRODUCTO:
                stock += convertir_unidades(producto.CANTIDAD, producto.PRODUCTO.UNIDAD_MEDIDA, self.UNIDAD_MEDIDA)
        return stock

    def stock_comprometido(self):
        stock = 0
        ventas = ingredientereceta.objects.filter(receta__ESTADO="Aceptado")
        for producto in ventas:
            if producto.producto == self:
                
                stock += producto.cantidad

        stock_a_descontar=0
        ventas_productos_compuestos = insumoCompuestoReceta.objects.filter(pedido__ESTADO="Aceptado")
        for venta in ventas_productos_compuestos:
            insumos = InsumoInsumoCompuesto.objects.filter(insumo_compuesto=venta.insumo_Compuesto,insumo=self)
            for insumo in insumos:
                if insumo.insumo == self:
                    stock_a_descontar += insumo.cantidad
            stock += stock_a_descontar * venta.cantidad
        
        return stock
    
    def stock_str(self):
        stock=self.stock_actual()
        return f'{stock} {self.UNIDAD_MEDIDA[:3]}'
        
def convertir_unidades(cantidad, unidad_origen, unidad_destino):
    unit_conversions = {
        'Litros': 1000,
        'Mililitros': 1,
        'Kilogramos': 1000,
        'Gramos': 1,
        'Unidades': 1,
        'Onzas': 1,
        'Libras': 1,
        'Mts': 1
    }
    
    if unidad_origen in unit_conversions and unidad_destino in unit_conversions:
        return cantidad * unit_conversions[unidad_origen] / unit_conversions[unidad_destino]
    return cantidad

class InsumoCompuesto(models.Model):
    DESCRIPCION = models.CharField(max_length=255,blank=False, null=False)
    CATEGORIA = models.ForeignKey(Categoria,on_delete=models.CASCADE,null=True, blank=True)
    UNIDADES_RESULTANTES = models.PositiveIntegerField(default=1,blank=False, null=False,verbose_name='PORCIONES RESULTANTES')
    RENTABILIDAD = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=False, null=False)
    PRECIO_VENTA_UNITARIO = models.DecimalField(max_digits=20, decimal_places=2,default=0, blank=True, null=False)
    HABILITAR_VENTA =models.BooleanField(default=False)

    def clean(self):

        prd = InsumoCompuesto.objects.count() or 0
        if prd > 15:
            raise ValidationError("Usted ha llegado al límite de items de la version DEMO.")
        
        if self.UNIDADES_RESULTANTES <= 0:
            raise ValidationError("Las unidades resultantes mínimas son 1.")
        if self.RENTABILIDAD < 0 or self.RENTABILIDAD > 99:
            raise ValidationError("La rentabilidad debe estar comprendida entre el 0% y el 99%")
        super().clean()

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural ='Productos Compuestos' 

    def __str__(self):
        return f'{self.DESCRIPCION}'

    def costo_unitario(self):
        precio = 0
        insumos_compuestos = InsumoInsumoCompuesto.objects.filter(insumo_compuesto=self)
        for producto in insumos_compuestos:
            if producto.insumo.UNIDAD_MEDIDA != producto.medida_uso:
                if producto.insumo.UNIDAD_MEDIDA == "Litros" or producto.insumo.UNIDAD_MEDIDA == "Kilogramos":
                    costo = producto.insumo.precio_venta() / 1000
                    precio += float(costo) * float(producto.cantidad)
                elif producto.insumo.UNIDAD_MEDIDA == "Mililitros" or producto.insumo.UNIDAD_MEDIDA == "Gramos":
                    costo = producto.insumo.precio_venta() * 1000
                    precio += float(costo) * float(producto.cantidad)
            else:
                costo = producto.insumo.precio_venta()
                precio += float(costo) * float(producto.cantidad)
        
        # Añadimos los costos de los InsumoCompuestoDetalle
        insumo_compuesto_detalles = InsumoCompuestoDetalle.objects.filter(insumo_compuesto_principal=self)
        for detalle in insumo_compuesto_detalles:
            precio += float(detalle.insumo_compuesto_referencia.costo_unitario()) * float(detalle.cantidad)

        precio = precio / self.UNIDADES_RESULTANTES
        return precio

    def costo_total(self):
        precio = self.costo_unitario() * self.UNIDADES_RESULTANTES
        return precio

    def precio_unitario(self):
        config = Configuracion.objects.first()
        if config.precios_automaticos:
            precio=self.costo_unitario()
            rentabilidad = float(self.RENTABILIDAD)
            if rentabilidad > 99 or rentabilidad < 0:
                precio = 0
            else:
                precio = float(float(precio)  / float(100 - rentabilidad) * 100)
        else:
            precio = self.PRECIO_VENTA_UNITARIO
        return precio
    
    def precio_total(self):
        precio = float(self.precio_unitario()) * float(self.UNIDADES_RESULTANTES)
        return precio

    def ganancias_limpias(self):
        costo = float(self.costo_unitario()) 
        precio_venta = float(self.precio_unitario()) 
        dif = float(float(precio_venta) - float(costo))
        return dif
    
    def rentabilidad(self):
        ganancias = self.ganancias_limpias() or 0
        p_venta = self.precio_unitario() or 0
        if p_venta > 0:
            rentabilidad = float(ganancias) / float(p_venta) * float(100)
        else:
            rentabilidad = 0
        return rentabilidad

    def stock_actual(self):

        stock = 0
        fabricaciones_confirmadas = Fabrica.objects.filter(RECETA=self, ESTADO="Finalizado")
        for fabricacion in fabricaciones_confirmadas:
            stock += fabricacion.UNIDADES_RESULTANTES * fabricacion.RECETA.UNIDADES_RESULTANTES

        ventas_productos_compuestos = insumoCompuestoReceta.objects.filter(insumo_Compuesto=self, pedido__ESTADO="Entregado")
        for venta in ventas_productos_compuestos:
            stock -= venta.cantidad

        insumos_compuestos_usados = InsumoInsumoCompuesto.objects.filter(insumo_compuesto_referencia=self)
        for insumo_usado in insumos_compuestos_usados:
            if insumo_usado.insumo_compuesto.HABILITAR_VENTA:
                stock -= insumo_usado.cantidad

        return stock

    def stock_str(self):
        stock = self.stock_actual()
        return f'{stock} Porciones'
    
class InsumoInsumoCompuesto(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, blank=True, null=True, related_name='insumo_insumo')
    insumo_compuesto = models.ForeignKey(InsumoCompuesto, related_name='insumo_principal', on_delete=models.CASCADE, blank=True, null=True)
    insumo_compuesto_referencia = models.ForeignKey(InsumoCompuesto, related_name='insumo_referencia', on_delete=models.CASCADE, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=20, decimal_places=3, default=1, blank=False, null=False)
    costo_unitario = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    medida_uso = models.CharField(max_length=10, choices=UnidadDeMedida, default="Unidades", null=False, blank=False)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'Insumo'
        verbose_name_plural = 'Carga de Insumos'

    def total(self):
        total = 0
        if self.insumo:
            total = self.insumo.precio_venta()

        # Convertir entre unidades si es necesario
        if self.medida_uso != self.insumo.UNIDAD_MEDIDA:
            if self.medida_uso in ["Kilogramos", "Litros"]:
                total = self.insumo.precio_venta() * 1000
            elif self.medida_uso in ["Gramos", "Mililitros"]:
                total = self.insumo.precio_venta() / 1000
            elif self.medida_uso == "Libras":
                total = self.insumo.precio_venta() / 16  # 1 libra = 16 onzas
            elif self.medida_uso == "Onzas":
                total = self.insumo.precio_venta() * 16  # 1 onza = 1/16 libra

        total = float(total) * float(self.cantidad)
        return total
    
    def clean(self):
        
        if self.insumo.UNIDAD_MEDIDA != self.medida_uso:
            if self.insumo.UNIDAD_MEDIDA == "Kilogramos":
                if self.medida_uso != "Gramos":
                    raise ValidationError("Si usas un insumo que esta en Kilos, debes usar Kilos o Gramos")
                
            if self.insumo.UNIDAD_MEDIDA == "Gramos":    
                if self.medida_uso != "Kilogramos":
                    raise ValidationError("Si usas un insumo que esta en Gramos, debes usar Kilos o Gramos")
                
            if self.insumo.UNIDAD_MEDIDA == "Litros":
                if self.medida_uso != "Mililitros":
                    raise ValidationError("Si usas un insumo que esta en Litros, debes usar Mililitros o Litros")
                
            if self.insumo.UNIDAD_MEDIDA == "Mililitros":    
                if self.medida_uso != "Litros":
                    raise ValidationError("Si usas un insumo que esta en Mililitros, debes usar Mililitros o Litros")

            if self.insumo.UNIDAD_MEDIDA == "Onzas":    
                if self.medida_uso != "Libras":
                    raise ValidationError("Si usas un insumo que esta en Onzas, debes usar Onzas o Libras")
                
            if self.insumo.UNIDAD_MEDIDA == "Libras":    
                if self.medida_uso != "Onzas":
                    raise ValidationError("Si usas un insumo que esta en Libras, debes usar Onzas o Libras")


        if self.cantidad <= 0:
            raise ValidationError("Por favor ingrese una cantidad superior a 0.")

        if not self.insumo and not self.insumo_compuesto_referencia:
            raise ValidationError("Debe tener un insumo o un insumo compuesto.")

        if self.insumo and self.insumo_compuesto_referencia:
            raise ValidationError("Un insumo compuesto no puede tener ambos insumos y insumos compuestos.")

        super().clean()

    def save(self, *args, **kwargs):

        if self.insumo:
            costo_unitario = self.insumo.costo_unitario()
            precio_unitario = self.insumo.precio_venta()


        if self.medida_uso != self.insumo.UNIDAD_MEDIDA:
            if self.medida_uso == "Kilogramos" or self.medida_uso == "Litros":
                costo_unitario = self.insumo.costo_unitario()
                precio_unitario = self.insumo.precio_venta()
            elif self.medida_uso == "Gramos" or self.medida_uso == "Mililitros":
                costo_unitario = self.insumo.costo_unitario()
                precio_unitario = self.insumo.precio_venta()       
            
        self.costo_unitario = costo_unitario
        self.precio_unitario = precio_unitario
        self.subtotal = float(precio_unitario) * float(self.cantidad)

        super().save(*args, **kwargs)

    def subtotal_actual(self):
        precio = self.insumo.costo_unitario()
        cantidad  = self.cantidad
        subtotal= float(precio) * float(cantidad)
        return subtotal

class InsumoCompuestoDetalle(models.Model):
    insumo_compuesto_principal = models.ForeignKey(InsumoCompuesto, related_name='detalle_principal', on_delete=models.CASCADE)
    insumo_compuesto_referencia = models.ForeignKey(InsumoCompuesto, related_name='detalle_referencia', on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=20, decimal_places=3, default=1, blank=False, null=False)
    
    class Meta:
        verbose_name = 'Detalle de Insumo Compuesto'
        verbose_name_plural = 'Detalles de Insumos Compuestos'

    def __str__(self):
        return f'{self.insumo_compuesto_principal} - {self.insumo_compuesto_referencia}'

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("Por favor ingrese una cantidad superior a 0.")
        super().clean()

class Pedido(models.Model):
    FECHA = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    ESTADO= models.CharField(choices=Estado,max_length=20,default="Pendiente",blank=False,null=False)
    CLIENTE = models.ForeignKey(Cliente, on_delete=models.CASCADE,blank=False,null=False,default=1)
    FECHA_ENTREGA = models.DateField(null=True, blank=False,default=timezone.now)
    VALIDO_HASTA = models.DateField(blank=True,null=True)
    DESCUENTO = models.FloatField(default=0, blank=False, null=False)
    ULTIMA_ACTUALIZACION = models.DateTimeField(blank=True,null=True,auto_now=True)
    
    def __str__(self):
        return f'Pedido #{self.pk} | Cliente: {self.CLIENTE} | Total $ {self.precio_total()}'

    def clean(self):
        prd = Pedido.objects.count() or 0
        if prd > 20:
            raise ValidationError("Usted ha llegado al límite de pedidos de la version DEMO.")
      
        if self.pk:
            if self.ESTADO == "Entregado" or self.ESTADO == "Aceptado":
                raise ValidationError("No se puede modificar un pedido Aceptado/Entregado")
        if self.DESCUENTO < 0:
            raise ValidationError("El descuento no puede ser negarivo.")
        super().clean()

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural ='Presupuestos' 

    def precio_total(self):
        costo = 0
        if self.ESTADO == "Pendiente":
            for ingrediente in self.ingredientereceta_set.all():
                costo += float((float(round(ingrediente.producto.precio_venta(),2)) * float(ingrediente.cantidad)) - float(ingrediente.descuento)) or 0
            for ingrediente in self.insumocompuestoreceta_set.all():
                costo += float(round(float(ingrediente.insumo_Compuesto.precio_unitario()) * float(ingrediente.cantidad),2)) or 0
        else:
            for ingrediente in self.ingredientereceta_set.all():
                costo += float(ingrediente.subtotal) or 0
            for ingrediente in self.insumocompuestoreceta_set.all():
                costo += float(ingrediente.subtotal) or 0

        descuento = self.DESCUENTO
        precio_final = round(costo - descuento,2)
        return max(precio_final, 0)
    
    def save(self, *args, **kwargs):

        if not self.pk:
            self.FECHA = datetime.datetime.now() - datetime.timedelta(hours=3)
        super().save(*args, **kwargs)

    def check_pagos(self):
        if self.precio_total() == self.Total_Pagos:
            return True
        else:
            return False  
        
    def ventas_total(fecha_desde):
        
        total=0
     
        ventas = Pedido.objects.filter(FECHA=fecha_desde)

        for venta in ventas:
            total += venta.precio_total()

        return total 

    @property
    def Total_Costos(self):
        precio = 0
        for ingrediente in self.ingredientereceta_set.all():
            precio += float(ingrediente.costo_unitario) * float(ingrediente.cantidad)
        return round(precio,2)

    @property
    def Total_Pagos(self):
        precio = 0
        for detalle in self.pagospedidos_set.all():
            precio += float(detalle.TOTAL)
        return round(precio,2)

    @property
    def ganancias_estimadas(self):
        ganancias = self.Total_Pagos - self.Total_Costos

        return round(ganancias,2)

    @classmethod
    def ventas_ultimos(cls):
        ventas_dias = []
        fecha_hoy = timezone.now().date()

        for x in range(15):
            fecha = fecha_hoy - datetime.timedelta(days=x)
            ventas = cls.objects.filter(FECHA__date=fecha)
            total_ventas_dia = sum(venta.precio_total() for venta in ventas)
            total_ganancias_dia = sum(venta.ganancias_estimadas for venta in ventas)
            ventas_dias.append((fecha, total_ventas_dia, total_ganancias_dia))

        return ventas_dias

class ingredientereceta(models.Model):

    producto  = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    receta = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    costo_unitario = models.DecimalField(max_digits=20, decimal_places=2,blank=True,null=True)
    precio_unitario = models.DecimalField(max_digits=20, decimal_places=2,blank=True,null=True)
    medida_uso = models.CharField(max_length=255,blank=True,null=True)
    descuento = models.DecimalField(max_digits=20, decimal_places=2,default=0,blank=False,null=False)
    subtotal = models.DecimalField(max_digits=20,decimal_places=2,default=0,blank=False,null=False)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural ='Productos incluidos en presupuesto' 

    def __str__(self):
        return "-"
    
    def clean(self):

        if self.cantidad <= 0:
            raise ValidationError("Por favor ingrese una cantidad superior a 0.")

        precio = float(self.producto.precio_venta()) * float(self.cantidad)
        ganancia = float(self.producto.ganancias_limpias()) * float(self.cantidad)
        descuentos = float(self.descuento) 
        
        if descuentos > precio:
            raise ValidationError("El descuento no puede ser superior al subtotal.")
        if self.descuento < 0:
            raise ValidationError("El descuento no puede ser un importe negativo.")
        if descuentos > ganancia:
            raise ValidationError("El descuento supera el permitido.")  
        
        super().clean()

    def save(self, *args, **kwargs):
        costo_unitario = float(self.producto.costo_unitario())
        self.costo_unitario = costo_unitario
        precio_unitario = float(self.producto.precio_venta())
        self.precio_unitario = float(precio_unitario)
        self.medida_uso = self.producto.UNIDAD_MEDIDA
        self.subtotal = (float(precio_unitario) * float(self.cantidad)) - float(self.descuento)
        super().save(*args, **kwargs)

    @property
    def ganancias(self):
        costos = float(self.costo_unitario) * float(self.cantidad)
        subtotal = float(costos) * float(self.subtotal)
        return subtotal
    
class insumoCompuestoReceta(models.Model):

    pedido  = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    insumo_Compuesto = models.ForeignKey(InsumoCompuesto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    precio_unitario_back = models.DecimalField(max_digits=20, decimal_places=2,blank=True,null=True,default=0)
    subtotal = models.DecimalField(max_digits=20,decimal_places=2,default=0,blank=False,null=False)

    class Meta:
        verbose_name = 'Producto compuesto'
        verbose_name_plural ='Productos Compuesto incluidos' 

    def __str__(self):
        return "-"
    
    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("Por favor ingrese una cantidad superior a 0.")
        super().clean()

    def save(self, *args, **kwargs):
      
        precio_unitario = float(self.insumo_Compuesto.precio_unitario())
        self.precio_unitario_back = precio_unitario
        self.medida_uso = "Unidades"
        self.subtotal = float(precio_unitario) * float(self.cantidad)

        super().save(*args, **kwargs)

    def precio(self):
        if self.pedido.ESTADO == "Pendiente":
            precio = self.insumo_Compuesto.precio_unitario()
        else:
            precio = self.precio_unitario_back
        return precio

    def total(self):
        if self.pedido.ESTADO == "Pendiente":
            precio = self.insumo_Compuesto.precio_unitario()
            cantidad = self.cantidad
            total = round(float(precio * cantidad),2)
        else:
            total = float(self.subtotal)
        return total

class Gastos(models.Model):
    FECHA = models.DateField(blank=True,null=True,)
    DETALLE  = models.CharField(max_length=255,blank=False,null=False)
    TOTAL = models.DecimalField(max_digits=20, decimal_places=2,blank=False,null=False)
    
    def clean(self):
        if self.TOTAL and self.TOTAL < 0:
            raise ValidationError("Por favor ingrese un monto superior a 0.")
        super().clean()

    class Meta:
        verbose_name = 'gasto'
        verbose_name_plural ='Gastos fijos' 

class Compras(models.Model):
    FECHA = models.DateTimeField(auto_now_add=True,blank=True,null=True,)
    PROVEEDOR = models.ForeignKey(Proveedor, on_delete=models.PROTECT,blank=True,null=True,verbose_name='Proveedor')
    ESTADO = models.BooleanField(default=False)

    def __str__(self):
        return f'Pedido #{self.pk} | Total Compra $ {self.Total}'

    def clean(self):

        if self.ESTADO == True:
            raise ValidationError("La compra está confirmada y no puede modificarse.")  

        super().clean()
    
    @property
    def Total(self):
        
        precio = 0
        for detalle in self.detallecompra_set.all():
            precio += float(detalle.CANTIDAD) * (float(detalle.PRECIO) - ( float(detalle.PRECIO) * float(detalle.DESCUENTO) /100))

        return precio
    
    def check_pagos(self):
        a = round(float(self.Total),0)
        b = round(float(self.Total_Pagos),0)
        if a == b:
            return True
        else:
            return False  

    @property
    def Total_Pagos(self):
        precio = 0
        for detalle in self.pagoscompras_set.all():
            precio += float(detalle.TOTAL)
        return precio

class DetalleCompra(models.Model): 
    FECHA = models.DateField(auto_now_add=True)
    COMPRA = models.ForeignKey(Compras, on_delete=models.CASCADE)
    PRODUCTO = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    CANTIDAD = models.DecimalField(max_digits=25, decimal_places=2,default=1)
    PRECIO = models.DecimalField(verbose_name="Precio unitario",max_digits=25,decimal_places=2,default=0)
    DESCUENTO = models.DecimalField(verbose_name="Desc (%)",max_digits=5, decimal_places=2,default=0)
    ActualizarCosto = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'detalle de compra'
        verbose_name_plural = 'Detalles de compras'

    def clean(self):
        prd = DetalleCompra.objects.count() or 0
        if prd > 50:
            raise ValidationError("Usted ha llegado al límite de items de la version DEMO.")
        
        if self.COMPRA.ESTADO == True:
            raise ValidationError("La compra está confirmada y no puede modificarse.")  
        
        if self.DESCUENTO > 100:
            raise ValidationError("El descuento no puede ser superior a 100%.")
        
        if self.DESCUENTO < 0:
            raise ValidationError("El descuento debe ser superior o igual a 0%.")
        
        super().clean()
    
    def save(self, *args, **kwargs):
        
        PRECIO = float(self.PRECIO)
        DESCUENTO = (PRECIO * float(self.DESCUENTO) / 100)
        self.TOTAL = float(PRECIO - DESCUENTO) * float(self.CANTIDAD)

        super().save(*args, **kwargs)

        super(DetalleCompra, self).save(*args, **kwargs)

    @property
    def Total(self):
        PRECIO = float(self.PRECIO)
        DESCUENTO = (PRECIO * float(self.DESCUENTO) / 100)
        TOTAL = float(PRECIO - DESCUENTO) * float(self.CANTIDAD)
        return TOTAL

    def __str__(self):
        return "-"

class PagosCompras(models.Model):
    COMPRA = models.ForeignKey(Compras,on_delete=models.CASCADE,blank=True,null=True,)
    PROVEEDOR = models.ForeignKey(Proveedor, on_delete=models.PROTECT,blank=True,null=True,verbose_name='Proveedor')
    MEDIO_DE_PAGO = models.ForeignKey(medioDePago,on_delete=models.CASCADE,blank=False,null=False)
    TOTAL = models.DecimalField(max_length=25, decimal_places=2,default=0, max_digits=10, null=True)

    class Meta:
        verbose_name = 'pago'  # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='seccion de pagos' # Como se nombra el modelo

    def clean(self):
        configuracion = Configuracion.objects.all().first()
        if not self.COMPRA:
            if str(self.MEDIO_DE_PAGO).upper() == "CUENTA CORRIENTE":
                raise ValidationError(f'Seleccione un metodo de pago diferente a Cuenta Corriente.')

            proveedor = Proveedor.objects.filter(id=self.PROVEEDOR.id).first()

            saldo = 0
            saldo = proveedor.cuenta_corriente

            if self.TOTAL > saldo:
                raise ValidationError(f'El pago no puede ser mayor a la cuenta corrriente. CC Actual: {configuracion.moneda} {saldo:,.2f}')

            if self.TOTAL <= 0:
                raise ValidationError(f'Ingrese un pago superior a 0.')

        
        super().clean()

    def save(self, *args, **kwargs):
        super(PagosCompras, self).save(*args, **kwargs)
        
        def __str__(self):
            return "-"

class PagosPedidos(models.Model):
    PEDIDO = models.ForeignKey(Pedido,on_delete=models.CASCADE,blank=True,null=True)
    CLIENTE = models.ForeignKey(Cliente,on_delete=models.CASCADE,default=1,blank=False,null=False)
    MEDIO_DE_PAGO = models.ForeignKey(medioDePago,on_delete=models.CASCADE,blank=False,null=False,default=1)
    TOTAL = models.DecimalField(max_length=25, decimal_places=2,default=0, max_digits=10,blank=False, null=False)

    class Meta:
        verbose_name = 'pago'
        verbose_name_plural ='seccion de pagos'

    def clean(self):

        if str(self.MEDIO_DE_PAGO).upper() == "CUENTA CORRIENTE":
            if not self.PEDIDO:
                raise ValidationError(f'No se puede realizar pagos en Cuenta Corriente.')
            else:
                if str(self.PEDIDO.CLIENTE.NOMBRE_Y_APELLIDO).upper() == "CONSUMIDOR FINAL":
                    raise ValidationError(f'Seleccione un cliente para abonar con Cuenta Corriente.')
                elif self.PEDIDO.CLIENTE.HABILITAR_CC == False:
                    raise ValidationError(f'El cliente no tiene habilitado el pago con Cuenta Corriente.')
             

        configuracion = Configuracion.objects.all().first()
        if not self.PEDIDO:
            if self.TOTAL < 0:
                raise ValidationError(f'Ingrese un total superior a $ 0')


            cliente = Cliente.objects.filter(pk=self.CLIENTE.pk).first()

            saldo = 0
            saldo = cliente.Cuenta_Corriente()

            if self.TOTAL > saldo:
                raise ValidationError(f'El pago no puede ser mayor a la cuenta corrriente. CC Actual: {configuracion.moneda} {saldo:,.2f}')

            if self.TOTAL <= 0:
                raise ValidationError(f'Ingrese un pago superior a 0.')

        super().clean()

    def save(self, *args, **kwargs):

        # if self.PEDIDO.CLIENTE:
        #     self.CLIENTE = self.PEDIDO.CLIENTE

        super(PagosPedidos, self).save(*args, **kwargs)

    def __str__(self):
        return "-"

class ComentarioVenta(models.Model): 
    VENTA = models.ForeignKey(Pedido,on_delete=models.CASCADE)
    FECHA = models.DateTimeField(auto_now_add=True)
    COMENTARIO = models.CharField(max_length=255,verbose_name="Comentarios")
    
    class Meta:
        verbose_name = 'comentarios'
        verbose_name_plural ='Comentarios' 
        
    def __str__(self):

        fecha_formateada = self.FECHA - datetime.timedelta(hours=3)

        # Formatear la fecha a "15 de Enero 15:35 PM"
        fecha_formateada = fecha_formateada.strftime("%d de %B %H:%M %p")
        
        # Convertir el nombre del mes a mayúsculas
        partes_fecha = fecha_formateada.split(' ')
        partes_fecha[1] = partes_fecha[1].upper()  # Mes en mayúsculas
        
        # Convertir AM/PM a minúsculas
        partes_fecha[-1] = partes_fecha[-1].lower()
        
        # Reconstruir la fecha formateada
        fecha_final = ' '.join(partes_fecha)
        
        return fecha_final

class Fabrica(models.Model):
    FECHA = models.DateTimeField(blank=True,null=True,default=timezone.now)
    ESTADO= models.CharField(choices=Estado_fabrica,max_length=20,default="Pendiente",blank=False,null=False)
    RECETA = models.ForeignKey(InsumoCompuesto,on_delete=models.CASCADE,blank=False,null=False)
    UNIDADES_RESULTANTES = models.PositiveIntegerField(default=1,blank=False, null=False,verbose_name='PORCIONES RESULTANTES')
    VALIDO_HASTA = models.DateField(blank=True,null=True)

    def __str__(self):
        return f'Fabrica #{self.pk} | Receta: {self.RECETA} | Unidades Resultantes: {self.UNIDADES_RESULTANTES}'

    def clean(self):
        if self.pk:
            if self.ESTADO == "Finalizado":
                raise ValidationError("No se puede modificar una fabricación finalizada.")
        super().clean()

    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Fabricaciones' 

    def control_insumos(self):

        fabricar_negativo = Configuracion.objects.first().fabricar_negativo
        insumos_necesarios = InsumoInsumoCompuesto.objects.filter(insumo_compuesto=self.RECETA)
        insumos_faltantes = []

        for insumo in insumos_necesarios:
            
            cantidad_total_necesaria = insumo.cantidad * self.UNIDADES_RESULTANTES

            if insumo.insumo.UNIDAD_MEDIDA != insumo.medida_uso:

                if insumo.medida_uso == "Kilogramos" or insumo.medida_uso == "Litros":
                    cantidad_disponible = insumo.insumo.stock_actual() / 1000
                elif insumo.medida_uso == "Gramos" or insumo.medida_uso == "Mililitros":
                    cantidad_disponible = insumo.insumo.stock_actual() * 1000
            else:
                cantidad_total_necesaria = insumo.cantidad * self.UNIDADES_RESULTANTES
                cantidad_disponible = insumo.insumo.stock_actual()

            if cantidad_disponible < cantidad_total_necesaria:
                insumos_faltantes.append({
                    'insumo': insumo.insumo,
                    'cantidad_necesaria': cantidad_total_necesaria,
                    'cantidad_disponible': cantidad_disponible / unit_conversions[insumo.insumo.UNIDAD_MEDIDA]
                })

        if insumos_faltantes and fabricar_negativo == False:
            return False, insumos_faltantes
        return True, None

    def realizar_fabricacion(self):
        fabricar_negativo = Configuracion.objects.first().fabricar_negativo
        if fabricar_negativo == False:
            estado, insumos_faltantes = self.control_insumos()
        else:
            estado=True

        if estado:
            self.ESTADO = 'Finalizado'
            self.save()
            return True, "Fabricación realizada con éxito."
        else:
            return False, insumos_faltantes

class Dashboard(models.Model):
    nombre = models.CharField(max_length=255,blank=True,null=True)

class MiTienda(models.Model):
    nombre = models.CharField(max_length=255,blank=True,null=True)
