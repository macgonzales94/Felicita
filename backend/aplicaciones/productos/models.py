"""
Modelos de productos para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal
import os


class TipoProducto(models.TextChoices):
    """Tipos de producto según SUNAT"""
    BIEN = 'BIEN', 'Bien'
    SERVICIO = 'SERVICIO', 'Servicio'


class UnidadMedida(models.TextChoices):
    """Unidades de medida según SUNAT"""
    NIU = 'NIU', 'Unidad (NIU)'
    KGM = 'KGM', 'Kilogramo (KGM)'
    LTR = 'LTR', 'Litro (LTR)'
    MTR = 'MTR', 'Metro (MTR)'
    M2 = 'MTK', 'Metro cuadrado (MTK)'
    M3 = 'MTQ', 'Metro cúbico (MTQ)'
    GRM = 'GRM', 'Gramo (GRM)'
    TON = 'TON', 'Tonelada (TON)'
    ZZ = 'ZZ', 'Unidad de servicio (ZZ)'


class CodigoImpuesto(models.TextChoices):
    """Códigos de impuesto según SUNAT"""
    GRAVADO = '1000', 'IGV - Operación Gravada'
    EXONERADO = '9997', 'IGV - Operación Exonerada'
    INAFECTO = '9998', 'IGV - Operación Inafecta'
    EXPORTACION = '9995', 'IGV - Exportación'
    GRATUITO = '9996', 'IGV - Operación Gratuita'


class CategoriaProducto(models.Model):
    """
    Modelo para categorías de productos
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='categorias_productos',
        verbose_name='Empresa'
    )
    
    codigo = models.CharField(
        max_length=20,
        verbose_name='Código',
        help_text='Código único de la categoría'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    categoria_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name='Categoría Padre'
    )
    
    imagen = models.ImageField(
        upload_to='categorias/',
        blank=True,
        null=True,
        verbose_name='Imagen'
    )
    
    estado = models.BooleanField(
        default=True,
        verbose_name='Estado'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        db_table = 'categorias_productos'
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        unique_together = ['empresa', 'codigo']
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['categoria_padre']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def get_ruta_completa(self):
        """Obtener ruta completa de la categoría"""
        if self.categoria_padre:
            return f"{self.categoria_padre.get_ruta_completa()} > {self.nombre}"
        return self.nombre
    
    def get_subcategorias_activas(self):
        """Obtener subcategorías activas"""
        return self.subcategorias.filter(estado=True)
    
    def get_productos_activos(self):
        """Obtener productos activos de esta categoría"""
        return self.productos.filter(estado=True)
    
    def get_total_productos(self, incluir_subcategorias=True):
        """Obtener total de productos en la categoría"""
        total = self.productos.filter(estado=True).count()
        
        if incluir_subcategorias:
            for subcategoria in self.get_subcategorias_activas():
                total += subcategoria.get_total_productos(incluir_subcategorias=True)
        
        return total


class Producto(models.Model):
    """
    Modelo principal de productos
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='productos',
        verbose_name='Empresa'
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código',
        help_text='Código único del producto'
    )
    
    codigo_barra = models.CharField(
        max_length=50,
        blank=True,
        validators=[RegexValidator(
            regex=r'^[\d\-A-Za-z]+$',
            message='Código de barras inválido'
        )],
        verbose_name='Código de Barras'
    )
    
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre del Producto'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Categoría'
    )
    
    # Clasificación SUNAT
    codigo_sunat = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Código SUNAT',
        help_text='Código de producto según catálogo SUNAT'
    )
    
    tipo_producto = models.CharField(
        max_length=20,
        choices=TipoProducto.choices,
        default=TipoProducto.BIEN,
        verbose_name='Tipo de Producto'
    )
    
    unidad_medida = models.CharField(
        max_length=10,
        choices=UnidadMedida.choices,
        default=UnidadMedida.NIU,
        verbose_name='Unidad de Medida'
    )
    
    # Precios
    precio_compra = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Precio de Compra',
        help_text='Precio de compra sin IGV'
    )
    
    precio_venta = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Precio de Venta',
        help_text='Precio de venta sin IGV'
    )
    
    precio_venta_min = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Precio Mínimo de Venta',
        help_text='Precio mínimo permitido para venta'
    )
    
    margen_ganancia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Margen de Ganancia (%)',
        help_text='Margen de ganancia en porcentaje'
    )
    
    # Configuración de impuestos
    afecto_igv = models.BooleanField(
        default=True,
        verbose_name='Afecto a IGV',
        help_text='Si el producto está afecto al IGV'
    )
    
    codigo_impuesto = models.CharField(
        max_length=10,
        choices=CodigoImpuesto.choices,
        default=CodigoImpuesto.GRAVADO,
        verbose_name='Código de Impuesto'
    )
    
    # Control de inventario
    maneja_stock = models.BooleanField(
        default=True,
        verbose_name='Maneja Stock',
        help_text='Si el producto maneja control de inventario'
    )
    
    stock_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Stock Mínimo',
        help_text='Cantidad mínima en inventario'
    )
    
    stock_maximo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Stock Máximo',
        help_text='Cantidad máxima en inventario'
    )
    
    # Características físicas
    peso = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Peso (kg)',
        help_text='Peso del producto en kilogramos'
    )
    
    volumen = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.0000'))],
        verbose_name='Volumen (m³)',
        help_text='Volumen del producto en metros cúbicos'
    )
    
    # Multimedia
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name='Imagen Principal'
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones'
    )
    
    datos_adicionales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Datos Adicionales',
        help_text='Información adicional en formato JSON'
    )
    
    # Estado y auditoria
    estado = models.BooleanField(
        default=True,
        verbose_name='Estado',
        help_text='Si el producto está activo'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    usuario_creacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_creados',
        verbose_name='Usuario que Creó'
    )
    
    usuario_actualizacion = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_actualizados',
        verbose_name='Usuario que Actualizó'
    )
    
    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        unique_together = ['empresa', 'codigo']
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'codigo']),
            models.Index(fields=['codigo_barra']),
            models.Index(fields=['categoria']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_producto']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """Guardar producto con validaciones y cálculos automáticos"""
        # Calcular margen de ganancia si se especifica precio de compra
        if self.precio_compra > 0 and not self.margen_ganancia:
            self.margen_ganancia = (
                (self.precio_venta - self.precio_compra) / self.precio_compra * 100
            )
        
        # Calcular precio de venta basado en margen si no se especifica
        if self.precio_compra > 0 and self.margen_ganancia > 0 and not self.precio_venta:
            self.precio_venta = self.precio_compra * (1 + self.margen_ganancia / 100)
        
        # Validar precio mínimo
        if self.precio_venta_min and self.precio_venta_min > self.precio_venta:
            raise ValueError('El precio mínimo no puede ser mayor al precio de venta')
        
        super().save(*args, **kwargs)
    
    def get_precio_con_igv(self):
        """Obtener precio de venta con IGV incluido"""
        if self.afecto_igv:
            tasa_igv = self.empresa.get_tasa_igv()
            return self.precio_venta * (1 + tasa_igv)
        return self.precio_venta
    
    def get_precio_compra_con_igv(self):
        """Obtener precio de compra con IGV incluido"""
        if self.afecto_igv:
            tasa_igv = self.empresa.get_tasa_igv()
            return self.precio_compra * (1 + tasa_igv)
        return self.precio_compra
    
    def calcular_igv_unitario(self):
        """Calcular IGV unitario del producto"""
        if self.afecto_igv:
            tasa_igv = self.empresa.get_tasa_igv()
            return self.precio_venta * tasa_igv
        return Decimal('0.0000')
    
    def get_stock_total(self):
        """Obtener stock total en todos los almacenes"""
        if not self.maneja_stock:
            return None
        
        from aplicaciones.inventarios.models import Stock
        stock_total = Stock.objects.filter(
            producto=self,
            almacen__estado=True
        ).aggregate(
            total=models.Sum('cantidad_disponible')
        )['total']
        
        return stock_total or Decimal('0.0000')
    
    def get_stock_por_almacen(self):
        """Obtener stock por almacén"""
        if not self.maneja_stock:
            return {}
        
        from aplicaciones.inventarios.models import Stock
        stocks = Stock.objects.filter(
            producto=self,
            almacen__estado=True
        ).select_related('almacen')
        
        return {
            stock.almacen.nombre: stock.cantidad_disponible
            for stock in stocks
        }
    
    def tiene_stock_suficiente(self, cantidad, almacen=None):
        """Verificar si hay stock suficiente"""
        if not self.maneja_stock:
            return True
        
        if almacen:
            from aplicaciones.inventarios.models import Stock
            try:
                stock = Stock.objects.get(producto=self, almacen=almacen)
                return stock.cantidad_disponible >= cantidad
            except Stock.DoesNotExist:
                return False
        else:
            return self.get_stock_total() >= cantidad
    
    def necesita_reposicion(self):
        """Verificar si el producto necesita reposición"""
        if not self.maneja_stock or self.stock_minimo <= 0:
            return False
        
        stock_actual = self.get_stock_total() or Decimal('0.0000')
        return stock_actual <= self.stock_minimo
    
    def get_valor_inventario(self):
        """Obtener valor total del inventario del producto"""
        if not self.maneja_stock:
            return Decimal('0.00')
        
        from aplicaciones.inventarios.models import Stock
        valor_total = Stock.objects.filter(
            producto=self,
            almacen__estado=True
        ).aggregate(
            total=models.Sum('valor_total')
        )['total']
        
        return valor_total or Decimal('0.00')
    
    def get_costo_promedio(self):
        """Obtener costo promedio ponderado"""
        if not self.maneja_stock:
            return self.precio_compra
        
        from aplicaciones.inventarios.models import Stock
        stock_info = Stock.objects.filter(
            producto=self,
            almacen__estado=True,
            cantidad_disponible__gt=0
        ).aggregate(
            cantidad_total=models.Sum('cantidad_disponible'),
            valor_total=models.Sum('valor_total')
        )
        
        if stock_info['cantidad_total'] and stock_info['valor_total']:
            return stock_info['valor_total'] / stock_info['cantidad_total']
        
        return self.precio_compra
    
    def get_datos_para_comprobante(self):
        """Obtener datos formateados para uso en comprobantes"""
        return {
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'unidad_medida': self.unidad_medida,
            'precio_unitario': self.precio_venta,
            'afecto_igv': self.afecto_igv,
            'codigo_impuesto': self.codigo_impuesto,
            'tipo_producto': self.tipo_producto,
        }
    
    def clonar(self, nuevo_codigo, nuevo_nombre=None):
        """Crear una copia del producto con nuevo código"""
        nuevo_producto = Producto(
            empresa=self.empresa,
            codigo=nuevo_codigo,
            nombre=nuevo_nombre or f"{self.nombre} (Copia)",
            descripcion=self.descripcion,
            categoria=self.categoria,
            codigo_sunat=self.codigo_sunat,
            tipo_producto=self.tipo_producto,
            unidad_medida=self.unidad_medida,
            precio_compra=self.precio_compra,
            precio_venta=self.precio_venta,
            precio_venta_min=self.precio_venta_min,
            margen_ganancia=self.margen_ganancia,
            afecto_igv=self.afecto_igv,
            codigo_impuesto=self.codigo_impuesto,
            maneja_stock=self.maneja_stock,
            stock_minimo=self.stock_minimo,
            stock_maximo=self.stock_maximo,
            peso=self.peso,
            volumen=self.volumen,
            observaciones=self.observaciones,
            datos_adicionales=self.datos_adicionales.copy(),
        )
        
        nuevo_producto.save()
        return nuevo_producto
    
    def activar(self):
        """Activar producto"""
        self.estado = True
        self.save(update_fields=['estado'])
    
    def desactivar(self):
        """Desactivar producto"""
        self.estado = False
        self.save(update_fields=['estado'])
    
    @classmethod
    def buscar_por_codigo(cls, empresa, codigo):
        """Buscar producto por código"""
        return cls.objects.filter(
            empresa=empresa,
            codigo__iexact=codigo,
            estado=True
        ).first()
    
    @classmethod
    def buscar_por_codigo_barra(cls, empresa, codigo_barra):
        """Buscar producto por código de barras"""
        return cls.objects.filter(
            empresa=empresa,
            codigo_barra=codigo_barra,
            estado=True
        ).first()
    
    @classmethod
    def buscar_por_nombre(cls, empresa, nombre, limite=10):
        """Buscar productos por nombre"""
        return cls.objects.filter(
            empresa=empresa,
            nombre__icontains=nombre,
            estado=True
        )[:limite]
    
    @classmethod
    def obtener_con_stock_bajo(cls, empresa):
        """Obtener productos con stock bajo"""
        productos = cls.objects.filter(
            empresa=empresa,
            estado=True,
            maneja_stock=True,
            stock_minimo__gt=0
        )
        
        productos_stock_bajo = []
        for producto in productos:
            if producto.necesita_reposicion():
                productos_stock_bajo.append(producto)
        
        return productos_stock_bajo
    
    @classmethod
    def obtener_mas_vendidos(cls, empresa, limite=10):
        """Obtener productos más vendidos"""
        # Aquí se implementaría la lógica basada en histórico de ventas
        return cls.objects.filter(empresa=empresa, estado=True)[:limite]


class ImagenProducto(models.Model):
    """
    Modelo para múltiples imágenes de productos
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name='Producto'
    )
    
    imagen = models.ImageField(
        upload_to='productos/galeria/',
        verbose_name='Imagen'
    )
    
    descripcion = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Descripción'
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        db_table = 'imagenes_producto'
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Producto'
        ordering = ['orden', 'fecha_creacion']
    
    def __str__(self):
        return f"Imagen {self.orden} - {self.producto.nombre}"
    
    def delete(self, *args, **kwargs):
        """Eliminar archivo de imagen al borrar el registro"""
        if self.imagen and os.path.isfile(self.imagen.path):
            os.remove(self.imagen.path)
        super().delete(*args, **kwargs)