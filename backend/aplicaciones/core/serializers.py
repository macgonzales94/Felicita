"""
SERIALIZERS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Serializers para la API REST del módulo core
"""

from rest_framework import serializers
from decimal import Decimal
from .models import (
    Empresa, Cliente, Proveedor, CategoriaProducto, 
    Producto, ConfiguracionSistema
)


# =============================================================================
# SERIALIZER BASE
# =============================================================================
class ModeloBaseSerializer(serializers.ModelSerializer):
    """
    Serializer base con campos comunes de auditoría
    """
    
    class Meta:
        fields = ['id', 'creado_en', 'actualizado_en', 'activo']
        read_only_fields = ['id', 'creado_en', 'actualizado_en']


# =============================================================================
# SERIALIZER EMPRESA
# =============================================================================
class EmpresaSerializer(ModeloBaseSerializer):
    """
    Serializer para el modelo Empresa
    """
    
    # Campos calculados
    nombre_completo = serializers.SerializerMethodField()
    es_ruc_valido = serializers.SerializerMethodField()
    
    class Meta:
        model = Empresa
        fields = [
            'id', 'ruc', 'razon_social', 'nombre_comercial',
            'direccion', 'ubigeo', 'distrito', 'provincia', 'departamento',
            'telefono', 'email', 'pagina_web',
            'plan_cuentas', 'moneda_base', 'regimen_tributario',
            'logo', 'nombre_completo', 'es_ruc_valido',
            'creado_en', 'actualizado_en', 'activo'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo de la empresa"""
        if obj.nombre_comercial:
            return f"{obj.razon_social} ({obj.nombre_comercial})"
        return obj.razon_social
    
    def get_es_ruc_valido(self, obj):
        """Valida el RUC con algoritmo SUNAT"""
        return obj.validar_ruc()
    
    def validate_ruc(self, value):
        """Validación personalizada del RUC"""
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("El RUC debe tener exactamente 11 dígitos")
        
        # Validar con algoritmo SUNAT
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(value[i]) * factores[i] for i in range(10))
        resto = suma % 11
        digito_verificador = 11 - resto if resto >= 2 else resto
        
        if digito_verificador != int(value[10]):
            raise serializers.ValidationError("RUC inválido según algoritmo SUNAT")
        
        return value
    
    def validate_email(self, value):
        """Validación personalizada del email"""
        if value and '@' not in value:
            raise serializers.ValidationError("Email inválido")
        return value


class EmpresaResumenSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listados de empresa
    """
    
    class Meta:
        model = Empresa
        fields = ['id', 'ruc', 'razon_social', 'nombre_comercial', 'email']


# =============================================================================
# SERIALIZER CLIENTE
# =============================================================================
class ClienteSerializer(ModeloBaseSerializer):
    """
    Serializer para el modelo Cliente
    """
    
    # Campos calculados
    nombre_completo = serializers.SerializerMethodField()
    documento_formato = serializers.SerializerMethodField()
    dias_vencimiento_promedio = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_documento', 'numero_documento', 'tipo_cliente',
            'razon_social', 'nombres', 'apellido_paterno', 'apellido_materno',
            'direccion', 'ubigeo', 'distrito', 'provincia', 'departamento',
            'telefono', 'email',
            'limite_credito', 'dias_credito', 'descuento_maximo',
            'bloqueado', 'fecha_bloqueo', 'motivo_bloqueo',
            'nombre_completo', 'documento_formato', 'dias_vencimiento_promedio',
            'creado_en', 'actualizado_en', 'activo'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del cliente"""
        return obj.get_nombre_completo()
    
    def get_documento_formato(self, obj):
        """Retorna el documento con formato"""
        return f"{obj.get_tipo_documento_display()}: {obj.numero_documento}"
    
    def get_dias_vencimiento_promedio(self, obj):
        """Calcula días promedio de vencimiento de facturas"""
        # TODO: Implementar cálculo basado en facturas
        return obj.dias_credito
    
    def validate_numero_documento(self, value):
        """Validación del número de documento"""
        tipo_documento = self.initial_data.get('tipo_documento', 'DNI')
        
        if tipo_documento == 'DNI':
            if not value.isdigit() or len(value) != 8:
                raise serializers.ValidationError("DNI debe tener exactamente 8 dígitos")
        
        elif tipo_documento == 'RUC':
            if not value.isdigit() or len(value) != 11:
                raise serializers.ValidationError("RUC debe tener exactamente 11 dígitos")
            
            # Validar RUC con algoritmo SUNAT
            factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            suma = sum(int(value[i]) * factores[i] for i in range(10))
            resto = suma % 11
            digito_verificador = 11 - resto if resto >= 2 else resto
            
            if digito_verificador != int(value[10]):
                raise serializers.ValidationError("RUC inválido según algoritmo SUNAT")
        
        return value
    
    def validate_limite_credito(self, value):
        """Validación del límite de crédito"""
        if value < 0:
            raise serializers.ValidationError("El límite de crédito no puede ser negativo")
        return value


class ClienteResumenSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listados de clientes
    """
    
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'numero_documento', 'razon_social', 'nombre_completo',
            'telefono', 'email', 'bloqueado'
        ]
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()


# =============================================================================
# SERIALIZER PROVEEDOR
# =============================================================================
class ProveedorSerializer(ModeloBaseSerializer):
    """
    Serializer para el modelo Proveedor
    """
    
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Proveedor
        fields = [
            'id', 'ruc', 'razon_social', 'nombre_comercial',
            'direccion', 'ubigeo', 'telefono', 'email', 'contacto_principal',
            'dias_pago', 'descuento_obtenido', 'activo_comercial',
            'nombre_completo',
            'creado_en', 'actualizado_en', 'activo'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del proveedor"""
        if obj.nombre_comercial:
            return f"{obj.razon_social} ({obj.nombre_comercial})"
        return obj.razon_social


# =============================================================================
# SERIALIZER CATEGORÍA PRODUCTO
# =============================================================================
class CategoriaProductoSerializer(ModeloBaseSerializer):
    """
    Serializer para el modelo CategoriaProducto
    """
    
    # Campos para jerarquía
    subcategorias = serializers.SerializerMethodField()
    nivel_jerarquia = serializers.SerializerMethodField()
    cantidad_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = CategoriaProducto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'categoria_padre',
            'subcategorias', 'nivel_jerarquia', 'cantidad_productos',
            'creado_en', 'actualizado_en', 'activo'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_subcategorias(self, obj):
        """Retorna las subcategorías"""
        subcategorias = obj.subcategorias.filter(activo=True)
        return CategoriaProductoResumenSerializer(subcategorias, many=True).data
    
    def get_nivel_jerarquia(self, obj):
        """Calcula el nivel en la jerarquía"""
        nivel = 1
        padre = obj.categoria_padre
        while padre:
            nivel += 1
            padre = padre.categoria_padre
        return nivel
    
    def get_cantidad_productos(self, obj):
        """Cuenta productos en esta categoría"""
        return obj.productos.filter(activo=True).count()


class CategoriaProductoResumenSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para categorías
    """
    
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'codigo', 'nombre']


# =============================================================================
# SERIALIZER PRODUCTO
# =============================================================================
class ProductoSerializer(ModeloBaseSerializer):
    """
    Serializer para el modelo Producto
    """
    
    # Información de la categoría
    categoria_info = CategoriaProductoResumenSerializer(source='categoria', read_only=True)
    
    # Campos calculados
    precio_con_igv = serializers.SerializerMethodField()
    precio_sin_igv = serializers.SerializerMethodField()
    margen_ganancia = serializers.SerializerMethodField()
    stock_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'codigo_barras', 'codigo_sunat',
            'nombre', 'descripcion', 'tipo_producto',
            'categoria', 'categoria_info', 'unidad_medida',
            'precio_compra', 'precio_venta', 'precio_venta_minimo',
            'tipo_afectacion_igv', 'incluye_igv',
            'controla_stock', 'stock_minimo',
            'marca', 'modelo', 'peso', 'imagen',
            'activo_venta', 'activo_compra',
            'precio_con_igv', 'precio_sin_igv', 'margen_ganancia', 'stock_actual',
            'creado_en', 'actualizado_en', 'activo'
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def get_precio_con_igv(self, obj):
        """Retorna el precio con IGV"""
        return float(obj.get_precio_con_igv())
    
    def get_precio_sin_igv(self, obj):
        """Retorna el precio sin IGV"""
        return float(obj.get_precio_sin_igv())
    
    def get_margen_ganancia(self, obj):
        """Calcula el margen de ganancia"""
        if obj.precio_compra > 0:
            margen = ((obj.precio_venta - obj.precio_compra) / obj.precio_compra) * 100
            return round(float(margen), 2)
        return 0.0
    
    def get_stock_actual(self, obj):
        """Obtiene el stock actual del producto"""
        # TODO: Implementar cuando se tenga el modelo StockProducto
        return 0.0
    
    def validate_codigo(self, value):
        """Validación del código de producto"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("El código debe tener al menos 3 caracteres")
        return value.upper().strip()
    
    def validate_precio_venta(self, value):
        """Validación del precio de venta"""
        if value <= 0:
            raise serializers.ValidationError("El precio de venta debe ser mayor a 0")
        
        precio_minimo = self.initial_data.get('precio_venta_minimo', 0)
        if precio_minimo and value < Decimal(str(precio_minimo)):
            raise serializers.ValidationError("El precio de venta no puede ser menor al precio mínimo")
        
        return value


class ProductoResumenSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para productos
    """
    
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    precio_con_igv = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'categoria_nombre',
            'precio_venta', 'precio_con_igv', 'unidad_medida',
            'activo_venta', 'controla_stock'
        ]
    
    def get_precio_con_igv(self, obj):
        return float(obj.get_precio_con_igv())


# =============================================================================
# SERIALIZER CONFIGURACIÓN SISTEMA
# =============================================================================
class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    """
    Serializer para configuraciones del sistema
    """
    
    valor_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = ConfiguracionSistema
        fields = [
            'id', 'clave', 'valor', 'descripcion', 'tipo_dato',
            'valor_formateado', 'actualizado_en'
        ]
        read_only_fields = ['id', 'actualizado_en']
    
    def get_valor_formateado(self, obj):
        """Retorna el valor formateado según su tipo"""
        if obj.tipo_dato == 'boolean':
            return obj.valor.lower() in ['true', '1', 'yes', 'on']
        elif obj.tipo_dato == 'integer':
            try:
                return int(obj.valor)
            except ValueError:
                return 0
        elif obj.tipo_dato == 'decimal':
            try:
                return float(obj.valor)
            except ValueError:
                return 0.0
        elif obj.tipo_dato == 'json':
            try:
                import json
                return json.loads(obj.valor)
            except (ValueError, TypeError):
                return {}
        return obj.valor
    
    def validate_valor(self, value):
        """Validación del valor según el tipo de dato"""
        tipo_dato = self.initial_data.get('tipo_dato', 'string')
        
        if tipo_dato == 'integer':
            try:
                int(value)
            except ValueError:
                raise serializers.ValidationError("El valor debe ser un número entero")
        
        elif tipo_dato == 'decimal':
            try:
                float(value)
            except ValueError:
                raise serializers.ValidationError("El valor debe ser un número decimal")
        
        elif tipo_dato == 'boolean':
            if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']:
                raise serializers.ValidationError("El valor debe ser verdadero o falso")
        
        elif tipo_dato == 'json':
            try:
                import json
                json.loads(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError("El valor debe ser JSON válido")
        
        return value


# =============================================================================
# SERIALIZERS PARA BÚSQUEDAS Y FILTROS
# =============================================================================
class BusquedaClienteSerializer(serializers.Serializer):
    """
    Serializer para búsqueda de clientes
    """
    
    termino = serializers.CharField(max_length=100, required=True)
    tipo_documento = serializers.ChoiceField(
        choices=['DNI', 'RUC', 'CE', 'PASSPORT', 'TODOS'],
        default='TODOS',
        required=False
    )
    incluir_bloqueados = serializers.BooleanField(default=False, required=False)


class BusquedaProductoSerializer(serializers.Serializer):
    """
    Serializer para búsqueda de productos
    """
    
    termino = serializers.CharField(max_length=100, required=True)
    categoria = serializers.UUIDField(required=False)
    solo_activos_venta = serializers.BooleanField(default=True, required=False)
    con_stock = serializers.BooleanField(default=False, required=False)