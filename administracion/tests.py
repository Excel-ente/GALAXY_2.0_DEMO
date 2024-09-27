from django.test import TestCase
from .models import Cliente, Proveedor, Insumo, InsumoCompuesto, Pedido, Compras, DetalleCompra, Fabrica, medioDePago, PagosCompras, PagosPedidos
from decimal import Decimal

class ClienteModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            NOMBRE_Y_APELLIDO='John Doe',
            DIRECCION='123 Main St',
            EMAIL='john@example.com',
            TELEFONO='1234567890',
            HABILITAR_CC=True
        )

    def test_crear_cliente(self):
        self.assertEqual(self.cliente.NOMBRE_Y_APELLIDO, 'John Doe')

    def test_cuenta_corriente_cliente(self):
        self.assertEqual(self.cliente.Cuenta_Corriente(), Decimal('0.00'))

class ProveedorModelTest(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            EMPRESA='Proveedor 1',
            NOMBRE='Jane Doe',
            DIRECCION='456 Main St',
            EMAIL='jane@example.com',
            TELEFONO='0987654321'
        )

    def test_crear_proveedor(self):
        self.assertEqual(self.proveedor.EMPRESA, 'Proveedor 1')

    # def test_cuenta_corriente_proveedor(self):
    #     self.assertEqual(self.proveedor.cuenta_corriente, Decimal('0.00'))

class InsumoModelTest(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            EMPRESA='Proveedor 1',
            NOMBRE='Jane Doe',
            DIRECCION='456 Main St',
            EMAIL='jane@example.com',
            TELEFONO='0987654321'
        )
        self.insumo = Insumo.objects.create(
            CODIGO='INS001',
            PRODUCTO='Insumo 1',
            PROVEEDOR=self.proveedor,
            CANTIDAD=10,
            UNIDAD_MEDIDA='Unidades',
            PRECIO_COMPRA=Decimal('100.00'),
            RENTABILIDAD=Decimal('20.00')
        )

    def test_crear_insumo(self):
        self.assertEqual(self.insumo.PRODUCTO, 'Insumo 1')

    def test_precio_venta_insumo(self):
        self.assertEqual(self.insumo.precio_venta(), Decimal('125.00'))

class PedidoModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            NOMBRE_Y_APELLIDO='John Doe',
            DIRECCION='123 Main St',
            EMAIL='john@example.com',
            TELEFONO='1234567890',
            HABILITAR_CC=True
        )
        self.medio_pago = medioDePago.objects.create(Nombre='Efectivo')
        self.pedido = Pedido.objects.create(
            CLIENTE=self.cliente,
            ESTADO='Pendiente',
            FECHA_ENTREGA='2024-07-01',
            DESCUENTO=Decimal('10.00')
        )

    def test_crear_pedido(self):
        self.assertEqual(self.pedido.CLIENTE, self.cliente)

    def test_precio_total_pedido(self):
        self.assertEqual(self.pedido.precio_total(), Decimal('0.00')) 

class FabricaModelTest(TestCase):
    def setUp(self):
        self.insumo_compuesto = InsumoCompuesto.objects.create(
            DESCRIPCION='Producto Compuesto 1',
            UNIDADES_RESULTANTES=10,
            RENTABILIDAD=Decimal('20.00'),
            HABILITAR_VENTA=True
        )
        self.fabrica = Fabrica.objects.create(
            RECETA=self.insumo_compuesto,
            UNIDADES_RESULTANTES=10
        )

    def test_crear_fabrica(self):
        self.assertEqual(self.fabrica.RECETA, self.insumo_compuesto)

    def test_control_insumos_fabrica(self):
        estado, insumos_faltantes = self.fabrica.control_insumos()
        self.assertTrue(estado)

class ComprasModelTest(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            EMPRESA='Proveedor 1',
            NOMBRE='Jane Doe',
            DIRECCION='456 Main St',
            EMAIL='jane@example.com',
            TELEFONO='0987654321'
        )
        self.compra = Compras.objects.create(
            PROVEEDOR=self.proveedor,
            ESTADO=False
        )

    def test_crear_compra(self):
        self.assertEqual(self.compra.PROVEEDOR, self.proveedor)

    def test_total_compra(self):
        self.assertEqual(self.compra.Total, Decimal('0.00'))

class PagosComprasModelTest(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            EMPRESA='Proveedor 1',
            NOMBRE='Jane Doe',
            DIRECCION='456 Main St',
            EMAIL='jane@example.com',
            TELEFONO='0987654321'
        )
        self.compra = Compras.objects.create(
            PROVEEDOR=self.proveedor,
            ESTADO=False
        )
        self.medio_pago = medioDePago.objects.create(
            Nombre='Transferencia Bancaria'
        )
        self.pago_compra = PagosCompras.objects.create(
            COMPRA=self.compra,
            PROVEEDOR=self.proveedor,
            MEDIO_DE_PAGO=self.medio_pago,
            TOTAL=Decimal('100.00')
        )

    def test_crear_pago_compra(self):
        self.assertEqual(self.pago_compra.PROVEEDOR, self.proveedor)
        self.assertEqual(self.pago_compra.TOTAL, Decimal('100.00'))

class PagosPedidosModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            NOMBRE_Y_APELLIDO='John Doe',
            DIRECCION='123 Main St',
            EMAIL='john@example.com',
            TELEFONO='1234567890',
            HABILITAR_CC=True
        )
        self.medio_pago = medioDePago.objects.create(Nombre='Efectivo')
        self.pedido = Pedido.objects.create(
            CLIENTE=self.cliente,
            ESTADO='Pendiente',
            FECHA_ENTREGA='2024-07-01',
            DESCUENTO=Decimal('10.00')
        )
        self.pago_pedido = PagosPedidos.objects.create(
            PEDIDO=self.pedido,
            CLIENTE=self.cliente,
            MEDIO_DE_PAGO=self.medio_pago,
            TOTAL=Decimal('50.00')
        )

    def test_crear_pago_pedido(self):
        self.assertEqual(self.pago_pedido.CLIENTE, self.cliente)
        self.assertEqual(self.pago_pedido.TOTAL, Decimal('50.00'))
