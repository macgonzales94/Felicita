"""
TESTS MODELS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Tests para los modelos del módulo core
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from django.utils import timezone

from ..models import (
    Empresa, Cliente, Proveedor, CategoriaProducto,
    Producto, ConfiguracionSistema
)


# =============================================================================
# TESTS BASE
# =============================================================================
class BaseTestCase(TestCase):
    """
    Clase base para tests con datos comunes
    """
    
    def setUp(self):
        """Configurar datos base para tests"""
        # Crear empresa de prueba
        self.empresa = Empresa.objects.create(
            ruc='20123456789',
            razon_social='EMPRESA PRUEBA S.A.C.',
            nombre_comercial='PRUEBA',
            direccion='AV. PRUEBA 123',
            ubigeo='150101',
            distrito='Lima',
            provincia='Lima',
            departamento='Lima',
            telefono='01-1234567',
            email='test@prueba.com'
        )
        
        # Crear categoría de prueba
        self.categoria = CategoriaProducto.objects.create(
            codigo='CAT001',
            nombre='Categoría Prueba',
            descripcion='Categoría para tests'
        )


# =============================================================================
# TESTS EMPRESA
# =============================================================================
class EmpresaModelTest(BaseTestCase):
    """
    Tests para el modelo Empresa
    """
    
    def test_crear_empresa_valida(self):
        """Test crear empresa con datos válidos"""
        empresa = Empresa.objects.create(
            ruc='20987654321',
            razon_social='NUEVA EMPRESA S.A.C.',
            direccion='AV. NUEVA 456',
            ubigeo='150122',
            distrito='Miraflores',
            provincia='Lima',
            departamento='Lima',
            email='nueva@empresa.com'
        )
        
        self.assertEqual(empresa.ruc, '20987654321')
        self.assertEqual(empresa.razon_social, 'NUEVA EMPRESA S.A.C.')
        self.assertTrue(empresa.activo)
    
    def test_ruc_unico(self):
        """Test que el RUC debe ser único"""
        with self.assertRaises(IntegrityError):
            Empresa.objects.create(
                ruc='20123456789',  # RUC duplicado
                razon_social='EMPRESA DUPLICADA',
                direccion='AV. DUPLICADA 789',
                ubigeo='150101',
                distrito='Lima',
                provincia='Lima',
                departamento='Lima',
                email='duplicada@empresa.com'
            )
    
    def test_validar_ruc_algoritmo(self):
        """Test validación de RUC con algoritmo SUNAT"""
        # RUC válido
        self.assertTrue(self.empresa.validar_ruc())
        
        # RUC inválido
        empresa_invalida = Empresa(ruc='20123456788')  # Último dígito incorrecto
        self.assertFalse(empresa_invalida.validar_ruc())
    
    def test_str_representation(self):
        """Test representación string de empresa"""
        expected = f"{self.empresa.ruc} - {self.empresa.razon_social}"
        self.assertEqual(str(self.empresa), expected)


# =============================================================================
# TESTS CLIENTE
# =============================================================================
class ClienteModelTest(BaseTestCase):
    """
    Tests para el modelo Cliente
    """
    
    def test_crear_cliente_persona_natural(self):
        """Test crear cliente persona natural"""
        cliente = Cliente.objects.create(
            tipo_documento='DNI',
            numero_documento='12345678',
            tipo_cliente='PERSONA_NATURAL',
            razon_social='JUAN PÉREZ GARCÍA',
            nombres='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            direccion='AV. CLIENTE 123',
            telefono='987654321',
            email='juan@email.com'
        )
        
        self.assertEqual(cliente.tipo_documento, 'DNI')
        self.assertEqual(cliente.tipo_cliente, 'PERSONA_NATURAL')
        self.assertTrue(cliente.activo)
        self.assertFalse(cliente.bloqueado)
    
    def test_crear_cliente_persona_juridica(self):
        """Test crear cliente persona jurídica"""
        cliente = Cliente.objects.create(
            tipo_documento='RUC',
            numero_documento='20555666777',
            tipo_cliente='PERSONA_JURIDICA',
            razon_social='EMPRESA CLIENTE S.A.C.',
            direccion='AV. EMPRESA 456',
            telefono='01-7654321',
            email='empresa@cliente.com'
        )
        
        self.assertEqual(cliente.tipo_documento, 'RUC')
        self.assertEqual(cliente.tipo_cliente, 'PERSONA_JURIDICA')
    
    def test_documento_unico_por_tipo(self):
        """Test que documento debe ser único por tipo"""
        # Crear primer cliente
        Cliente.objects.create(
            tipo_documento='DNI',
            numero_documento='87654321',
            tipo_cliente='PERSONA_NATURAL',
            razon_social='CLIENTE UNO',
            direccion='AV. UNO 123'
        )
        
        # Intentar crear segundo cliente con mismo documento
        with self.assertRaises(IntegrityError):
            Cliente.objects.create(
                tipo_documento='DNI',
                numero_documento='87654321',  # Documento duplicado
                tipo_cliente='PERSONA_NATURAL',
                razon_social='CLIENTE DOS',
                direccion='AV. DOS 456'
            )
    
    def test_get_nombre_completo_persona_natural(self):
        """Test obtener nombre completo de persona natural"""
        cliente = Cliente.objects.create(
            tipo_documento='DNI',
            numero_documento='11223344',
            tipo_cliente='PERSONA_NATURAL',
            razon_social='MARÍA GONZÁLEZ LÓPEZ',
            nombres='María',
            apellido_paterno='González',
            apellido_materno='López',
            direccion='AV. MARÍA 789'
        )
        
        expected = 'María González López'
        self.assertEqual(cliente.get_nombre_completo(), expected)
    
    def test_get_nombre_completo_persona_juridica(self):
        """Test obtener nombre completo de persona jurídica"""
        cliente = Cliente.objects.create(
            tipo_documento='RUC',
            numero_documento='20999888777',
            tipo_cliente='PERSONA_JURIDICA',
            razon_social='CORPORACIÓN XYZ S.A.C.',
            direccion='AV. CORPORACION 999'
        )
        
        expected = 'CORPORACIÓN XYZ S.A.C.'
        self.assertEqual(cliente.get_nombre_completo(), expected)
    
    def test_validar_documento_dni(self):
        """Test validación de DNI"""
        # DNI válido
        cliente_valido = Cliente(
            tipo_documento='DNI',
            numero_documento='12345678'
        )
        self.assertTrue(cliente_valido.validar_documento())
        
        # DNI inválido (no 8 dígitos)
        cliente_invalido = Cliente(
            tipo_documento='DNI',
            numero_documento='1234567'
        )
        self.assertFalse(cliente_invalido.validar_documento())
    
    def test_validar_documento_ruc(self):
        """Test validación de RUC"""
        # RUC válido
        cliente_valido = Cliente(
            tipo_documento='RUC',
            numero_documento='20123456789'
        )
        self.assertTrue(cliente_valido.validar_documento())
        
        # RUC inválido (no 11 dígitos)
        cliente_invalido = Cliente(
            tipo_documento='RUC',
            numero_documento='201234567'
        )
        self.assertFalse(cliente_invalido.validar_documento())


# =============================================================================
# TESTS PROVEEDOR
# =============================================================================
class ProveedorModelTest(BaseTestCase):
    """
    Tests para el modelo Proveedor
    """
    
    def test_crear_proveedor_valido(self):
        """Test crear proveedor con datos válidos"""
        proveedor = Proveedor.objects.create(
            ruc='20147852369',
            razon_social='PROVEEDOR PRUEBA S.A.C.',
            nombre_comercial='PROVPRUEBA',
            direccion='AV. PROVEEDOR 123',
            telefono='01-9876543',
            email='proveedor@prueba.com',
            contacto_principal='Juan Proveedor',
            dias_pago=30,
            descuento_obtenido=Decimal('5.00')
        )
        
        self.assertEqual(proveedor.ruc, '20147852369')
        self.assertEqual(proveedor.razon_social, 'PROVEEDOR PRUEBA S.A.C.')
        self.assertTrue(proveedor.activo)
        self.assertTrue(proveedor.activo_comercial)
    
    def test_ruc_proveedor_unico(self):
        """Test que el RUC del proveedor debe ser único"""
        # Crear primer proveedor
        Proveedor.objects.create(
            ruc='20111222333',
            razon_social='PROVEEDOR UNO',
            direccion='AV. UNO 123'
        )
        
        # Intentar crear segundo proveedor con mismo RUC
        with self.assertRaises(IntegrityError):
            Proveedor.objects.create(
                ruc='20111222333',  # RUC duplicado
                razon_social='PROVEEDOR DOS',
                direccion='AV. DOS 456'
            )


# =============================================================================
# TESTS CATEGORÍA PRODUCTO
# =============================================================================
class CategoriaProductoModelTest(BaseTestCase):
    """
    Tests para el modelo CategoriaProducto
    """
    
    def test_crear_categoria_valida(self):
        """Test crear categoría con datos válidos"""
        categoria = CategoriaProducto.objects.create(
            codigo='CAT002',
            nombre='Nueva Categoría',
            descripcion='Descripción de la categoría'
        )
        
        self.assertEqual(categoria.codigo, 'CAT002')
        self.assertEqual(categoria.nombre, 'Nueva Categoría')
        self.assertTrue(categoria.activo)
    
    def test_codigo_categoria_unico(self):
        """Test que el código de categoría debe ser único"""
        with self.assertRaises(IntegrityError):
            CategoriaProducto.objects.create(
                codigo='CAT001',  # Código duplicado
                nombre='Categoría Duplicada'
            )
    
    def test_jerarquia_categorias(self):
        """Test jerarquía de categorías padre-hijo"""
        subcategoria = CategoriaProducto.objects.create(
            codigo='SUBCAT001',
            nombre='Subcategoría',
            categoria_padre=self.categoria
        )
        
        self.assertEqual(subcategoria.categoria_padre, self.categoria)
        self.assertIn(subcategoria, self.categoria.subcategorias.all())


# =============================================================================
# TESTS PRODUCTO
# =============================================================================
class ProductoModelTest(BaseTestCase):
    """
    Tests para el modelo Producto
    """
    
    def test_crear_producto_valido(self):
        """Test crear producto con datos válidos"""
        producto = Producto.objects.create(
            codigo='PROD001',
            nombre='Producto Prueba',
            descripcion='Producto para testing',
            tipo_producto='BIEN',
            categoria=self.categoria,
            precio_compra=Decimal('10.00'),
            precio_venta=Decimal('15.00'),
            precio_venta_minimo=Decimal('12.00'),
            tipo_afectacion_igv='10',
            incluye_igv=True
        )
        
        self.assertEqual(producto.codigo, 'PROD001')
        self.assertEqual(producto.nombre, 'Producto Prueba')
        self.assertEqual(producto.categoria, self.categoria)
        self.assertTrue(producto.activo)
        self.assertTrue(producto.activo_venta)
    
    def test_codigo_producto_unico(self):
        """Test que el código del producto debe ser único"""
        # Crear primer producto
        Producto.objects.create(
            codigo='PROD002',
            nombre='Producto Uno',
            categoria=self.categoria,
            precio_venta=Decimal('10.00')
        )
        
        # Intentar crear segundo producto con mismo código
        with self.assertRaises(IntegrityError):
            Producto.objects.create(
                codigo='PROD002',  # Código duplicado
                nombre='Producto Dos',
                categoria=self.categoria,
                precio_venta=Decimal('20.00')
            )
    
    def test_get_precio_con_igv(self):
        """Test cálculo de precio con IGV"""
        # Producto con IGV incluido
        producto_con_igv = Producto.objects.create(
            codigo='PROD_IGV',
            nombre='Producto con IGV',
            categoria=self.categoria,
            precio_venta=Decimal('118.00'),
            incluye_igv=True
        )
        
        # El precio ya incluye IGV
        self.assertEqual(producto_con_igv.get_precio_con_igv(), Decimal('118.00'))
        
        # Producto sin IGV incluido
        producto_sin_igv = Producto.objects.create(
            codigo='PROD_SIN_IGV',
            nombre='Producto sin IGV',
            categoria=self.categoria,
            precio_venta=Decimal('100.00'),
            incluye_igv=False
        )
        
        # Debe calcular el IGV (100 * 1.18 = 118)
        self.assertEqual(producto_sin_igv.get_precio_con_igv(), Decimal('118.00'))
    
    def test_get_precio_sin_igv(self):
        """Test cálculo de precio sin IGV"""
        # Producto con IGV incluido
        producto_con_igv = Producto.objects.create(
            codigo='PROD_IGV2',
            nombre='Producto con IGV 2',
            categoria=self.categoria,
            precio_venta=Decimal('118.00'),
            incluye_igv=True
        )
        
        # Debe calcular sin IGV (118 / 1.18 = 100)
        precio_sin_igv = producto_con_igv.get_precio_sin_igv()
        self.assertEqual(precio_sin_igv, Decimal('100.00'))


# =============================================================================
# TESTS CONFIGURACIÓN SISTEMA
# =============================================================================
class ConfiguracionSistemaModelTest(TestCase):
    """
    Tests para el modelo ConfiguracionSistema
    """
    
    def test_crear_configuracion_valida(self):
        """Test crear configuración con datos válidos"""
        config = ConfiguracionSistema.objects.create(
            clave='TEST_CONFIG',
            valor='valor_test',
            descripcion='Configuración de prueba',
            tipo_dato='string'
        )
        
        self.assertEqual(config.clave, 'TEST_CONFIG')
        self.assertEqual(config.valor, 'valor_test')
        self.assertEqual(config.tipo_dato, 'string')
    
    def test_clave_unica(self):
        """Test que la clave debe ser única"""
        # Crear primera configuración
        ConfiguracionSistema.objects.create(
            clave='CLAVE_UNICA',
            valor='valor1'
        )
        
        # Intentar crear segunda configuración con misma clave
        with self.assertRaises(IntegrityError):
            ConfiguracionSistema.objects.create(
                clave='CLAVE_UNICA',  # Clave duplicada
                valor='valor2'
            )
    
    def test_obtener_valor_string(self):
        """Test obtener valor como string"""
        config = ConfiguracionSistema.objects.create(
            clave='STRING_TEST',
            valor='texto_prueba',
            tipo_dato='string'
        )
        
        valor = ConfiguracionSistema.obtener_valor('STRING_TEST')
        self.assertEqual(valor, 'texto_prueba')
    
    def test_obtener_valor_integer(self):
        """Test obtener valor como entero"""
        config = ConfiguracionSistema.objects.create(
            clave='INTEGER_TEST',
            valor='42',
            tipo_dato='integer'
        )
        
        valor = ConfiguracionSistema.obtener_valor('INTEGER_TEST')
        self.assertEqual(valor, 42)
        self.assertIsInstance(valor, int)
    
    def test_obtener_valor_decimal(self):
        """Test obtener valor como decimal"""
        config = ConfiguracionSistema.objects.create(
            clave='DECIMAL_TEST',
            valor='18.50',
            tipo_dato='decimal'
        )
        
        valor = ConfiguracionSistema.obtener_valor('DECIMAL_TEST')
        self.assertEqual(valor, Decimal('18.50'))
        self.assertIsInstance(valor, Decimal)
    
    def test_obtener_valor_boolean_true(self):
        """Test obtener valor booleano verdadero"""
        config = ConfiguracionSistema.objects.create(
            clave='BOOLEAN_TRUE_TEST',
            valor='true',
            tipo_dato='boolean'
        )
        
        valor = ConfiguracionSistema.obtener_valor('BOOLEAN_TRUE_TEST')
        self.assertTrue(valor)
        self.assertIsInstance(valor, bool)
    
    def test_obtener_valor_boolean_false(self):
        """Test obtener valor booleano falso"""
        config = ConfiguracionSistema.objects.create(
            clave='BOOLEAN_FALSE_TEST',
            valor='false',
            tipo_dato='boolean'
        )
        
        valor = ConfiguracionSistema.obtener_valor('BOOLEAN_FALSE_TEST')
        self.assertFalse(valor)
        self.assertIsInstance(valor, bool)
    
    def test_obtener_valor_json(self):
        """Test obtener valor como JSON"""
        config = ConfiguracionSistema.objects.create(
            clave='JSON_TEST',
            valor='{"clave": "valor", "numero": 123}',
            tipo_dato='json'
        )
        
        valor = ConfiguracionSistema.obtener_valor('JSON_TEST')
        expected = {"clave": "valor", "numero": 123}
        self.assertEqual(valor, expected)
        self.assertIsInstance(valor, dict)
    
    def test_obtener_valor_no_existe(self):
        """Test obtener valor que no existe"""
        valor = ConfiguracionSistema.obtener_valor('NO_EXISTE', 'valor_defecto')
        self.assertEqual(valor, 'valor_defecto')
    
    def test_str_representation(self):
        """Test representación string de configuración"""
        config = ConfiguracionSistema.objects.create(
            clave='STR_TEST',
            valor='valor_str'
        )
        
        expected = f"STR_TEST: valor_str"
        self.assertEqual(str(config), expected)