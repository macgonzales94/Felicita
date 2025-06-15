"""
FELICITA - Serializers Core
Sistema de Facturación Electrónica para Perú

Serializers para las entidades base del sistema
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import (
    Empresa, Sucursal, Cliente, Configuracion, 
    TipoComprobante, SerieComprobante
)
import logging

logger = logging.getLogger('felicita.core')

# ===========================================
# SERIALIZER BASE
# ===========================================

class BaseModelSerializer(serializers.ModelSerializer):
    """Serializer base con campos comunes"""
    
    fecha_creacion = serializers.DateTimeField(read_only=True, format='%d/%m/%Y %H:%M:%S')
    fecha_actualizacion = serializers.DateTimeField(read_only=True, format='%d/%m/%Y %H:%M:%S')
    
    def validate(self, attrs):
        """Validación personalizada"""
        # Crear instancia temporal para validaciones Django
        if self.instance:
            instance = self.instance
            for attr, value in attrs.items():
                setattr(instance, attr, value)
        else:
            instance = self.Meta.model(**attrs)
        
        try:
            instance.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else str(e))
        
        return attrs

# ===========================================
# EMPRESA SERIALIZERS
# ===========================================

class EmpresaSerializer(BaseModelSerializer):
    """Serializer para Empresa"""
    
    nombre_completo = serializers.CharField(read_only=True)
    esta_configurada_para_facturacion = serializers.BooleanField(read_only=True)
    total_sucursales = serializers.SerializerMethodField()
    total_clientes = serializers.SerializerMethodField()
    
    class Meta:
        model = Empresa
        fields = [
            'id', 'ruc', 'razon_social', 'nombre_comercial', 
            'direccion_fiscal', 'ubigeo', 'telefono', 'email',
            'representante_legal', 'usuario_sol', 'nombre_completo',
            'esta_configurada_para_facturacion', 'total_sucursales',
            'total_clientes', 'activo', 'fecha_creacion', 'fecha_actualizacion'
        ]
        extra_kwargs = {
            'clave_sol': {'write_only': True},
            'clave_certificado': {'write_only': True},
        }
    
    def get_total_sucursales(self, obj):
        """Obtener total de sucursales activas"""
        return obj.sucursales.filter(activo=True).count()
    
    def get_total_clientes(self, obj):
        """Obtener total de clientes activos"""
        return obj.clientes.filter(activo=True).count()
    
    def validate_ruc(self, value):
        """Validar RUC único"""
        if self.instance and self.instance.ruc == value:
            return value
            
        if Empresa.objects.filter(ruc=value, activo=True).exists():
            raise serializers.ValidationError("Ya existe una empresa con este RUC")
        
        return value

class EmpresaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de empresas"""
    
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Empresa
        fields = ['id', 'ruc', 'razon_social', 'nombre_completo', 'activo']

# ===========================================
# SUCURSAL SERIALIZERS
# ===========================================

class SucursalSerializer(BaseModelSerializer):
    """Serializer para Sucursal"""
    
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    
    class Meta:
        model = Sucursal
        fields = [
            'id', 'empresa', 'empresa_nombre', 'codigo', 'nombre',
            'direccion', 'ubigeo', 'telefono', 'email', 'es_principal',
            'activo', 'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def validate(self, attrs):
        """Validaciones personalizadas"""
        attrs = super().validate(attrs)
        
        # Validar código único por empresa
        empresa = attrs.get('empresa', self.instance.empresa if self.instance else None)
        codigo = attrs.get('codigo')
        
        if empresa and codigo:
            query = Sucursal.objects.filter(empresa=empresa, codigo=codigo, activo=True)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise serializers.ValidationError({
                    'codigo': 'Ya existe una sucursal con este código en la empresa'
                })
        
        return attrs

# ===========================================
# CLIENTE SERIALIZERS
# ===========================================

class ClienteSerializer(BaseModelSerializer):
    """Serializer para Cliente"""
    
    nombre_completo = serializers.CharField(read_only=True)
    es_empresa = serializers.BooleanField(read_only=True)
    saldo_pendiente = serializers.SerializerMethodField()
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'empresa', 'empresa_nombre', 'tipo_documento', 
            'numero_documento', 'razon_social', 'nombre_comercial',
            'direccion', 'ubigeo', 'telefono', 'email', 'contacto_principal',
            'limite_credito', 'dias_credito', 'nombre_completo', 'es_empresa',
            'saldo_pendiente', 'activo', 'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def get_saldo_pendiente(self, obj):
        """Obtener saldo pendiente del cliente"""
        return obj.obtener_saldo_pendiente()
    
    def validate(self, attrs):
        """Validaciones personalizadas"""
        attrs = super().validate(attrs)
        
        # Validar documento único por empresa
        empresa = attrs.get('empresa', self.instance.empresa if self.instance else None)
        numero_documento = attrs.get('numero_documento')
        
        if empresa and numero_documento:
            query = Cliente.objects.filter(
                empresa=empresa, 
                numero_documento=numero_documento, 
                activo=True
            )
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise serializers.ValidationError({
                    'numero_documento': 'Ya existe un cliente con este documento en la empresa'
                })
        
        return attrs

class ClienteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de clientes"""
    
    nombre_completo = serializers.CharField(read_only=True)
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_documento', 'tipo_documento_display', 
            'numero_documento', 'razon_social', 'nombre_completo', 
            'telefono', 'email', 'activo'
        ]

class ClienteSimpleSerializer(serializers.ModelSerializer):
    """Serializer muy simple para selects y autocompletado"""
    
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'numero_documento', 'razon_social', 'nombre_completo']

# ===========================================
# CONFIGURACIÓN SERIALIZERS
# ===========================================

class ConfiguracionSerializer(BaseModelSerializer):
    """Serializer para Configuración"""
    
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    moneda_defecto_display = serializers.CharField(source='get_moneda_defecto_display', read_only=True)
    metodo_valuacion_display = serializers.CharField(source='get_metodo_valuacion_display', read_only=True)
    
    class Meta:
        model = Configuracion
        fields = [
            'id', 'empresa', 'empresa_nombre', 'igv_porcentaje', 
            'moneda_defecto', 'moneda_defecto_display', 'numeracion_automatica',
            'envio_automatico_sunat', 'envio_email_cliente', 'metodo_valuacion',
            'metodo_valuacion_display', 'control_stock', 'formato_fecha',
            'parametros', 'activo', 'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def validate_igv_porcentaje(self, value):
        """Validar porcentaje IGV"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("El porcentaje debe estar entre 0 y 100")
        return value

# ===========================================
# TIPO COMPROBANTE SERIALIZERS
# ===========================================

class TipoComprobanteSerializer(BaseModelSerializer):
    """Serializer para Tipo de Comprobante"""
    
    total_series = serializers.SerializerMethodField()
    
    class Meta:
        model = TipoComprobante
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'requiere_serie',
            'formato_serie', 'total_series', 'activo', 
            'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def get_total_series(self, obj):
        """Obtener total de series para este tipo"""
        return obj.seriecomprobante_set.filter(activo=True).count()

class TipoComprobanteSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para selects"""
    
    class Meta:
        model = TipoComprobante
        fields = ['id', 'codigo', 'nombre']

# ===========================================
# SERIE COMPROBANTE SERIALIZERS
# ===========================================

class SerieComprobanteSerializer(BaseModelSerializer):
    """Serializer para Serie de Comprobante"""
    
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    tipo_comprobante_nombre = serializers.CharField(source='tipo_comprobante.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    siguiente_numero = serializers.SerializerMethodField()
    
    class Meta:
        model = SerieComprobante
        fields = [
            'id', 'empresa', 'empresa_nombre', 'tipo_comprobante', 
            'tipo_comprobante_nombre', 'serie', 'numero_actual',
            'siguiente_numero', 'sucursal', 'sucursal_nombre',
            'activo', 'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def get_siguiente_numero(self, obj):
        """Obtener siguiente número sin incrementar"""
        return obj.numero_actual + 1
    
    def validate(self, attrs):
        """Validaciones personalizadas"""
        attrs = super().validate(attrs)
        
        # Validar serie única por empresa y tipo
        empresa = attrs.get('empresa', self.instance.empresa if self.instance else None)
        tipo_comprobante = attrs.get('tipo_comprobante', self.instance.tipo_comprobante if self.instance else None)
        serie = attrs.get('serie')
        
        if empresa and tipo_comprobante and serie:
            query = SerieComprobante.objects.filter(
                empresa=empresa,
                tipo_comprobante=tipo_comprobante,
                serie=serie,
                activo=True
            )
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise serializers.ValidationError({
                    'serie': 'Ya existe esta serie para el tipo de comprobante en la empresa'
                })
        
        return attrs

class SerieComprobanteSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para selects"""
    
    tipo_nombre = serializers.CharField(source='tipo_comprobante.nombre', read_only=True)
    siguiente_numero = serializers.SerializerMethodField()
    
    class Meta:
        model = SerieComprobante
        fields = ['id', 'serie', 'tipo_nombre', 'numero_actual', 'siguiente_numero']
    
    def get_siguiente_numero(self, obj):
        return obj.numero_actual + 1

# ===========================================
# SERIALIZERS PARA VALIDACIONES APIS PERÚ
# ===========================================

class ValidarDocumentoSerializer(serializers.Serializer):
    """Serializer para validar documentos peruanos"""
    
    tipo_documento = serializers.ChoiceField(choices=[
        ('dni', 'DNI'),
        ('ruc', 'RUC'),
    ])
    numero_documento = serializers.CharField(max_length=11)
    
    def validate(self, attrs):
        """Validar documento según tipo"""
        tipo = attrs['tipo_documento']
        numero = attrs['numero_documento']
        
        if tipo == 'dni':
            if len(numero) != 8 or not numero.isdigit():
                raise serializers.ValidationError({
                    'numero_documento': 'DNI debe tener 8 dígitos numéricos'
                })
        elif tipo == 'ruc':
            if len(numero) != 11 or not numero.isdigit():
                raise serializers.ValidationError({
                    'numero_documento': 'RUC debe tener 11 dígitos numéricos'
                })
            
            # Validar dígito verificador RUC
            factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
            suma = sum(int(numero[i]) * factores[i] for i in range(10))
            resto = suma % 11
            digito_verificador = 11 - resto if resto >= 2 else resto
            
            if int(numero[10]) != digito_verificador:
                raise serializers.ValidationError({
                    'numero_documento': 'RUC no tiene un dígito verificador válido'
                })
        
        return attrs

# ===========================================
# SERIALIZERS PARA ESTADÍSTICAS
# ===========================================

class EstadisticasEmpresaSerializer(serializers.Serializer):
    """Serializer para estadísticas de empresa"""
    
    total_clientes = serializers.IntegerField()
    total_sucursales = serializers.IntegerField()
    total_series = serializers.IntegerField()
    clientes_activos = serializers.IntegerField()
    clientes_con_credito = serializers.IntegerField()
    configuracion_completa = serializers.BooleanField()

class EstadisticasGeneralesSerializer(serializers.Serializer):
    """Serializer para estadísticas generales del sistema"""
    
    total_empresas = serializers.IntegerField()
    empresas_activas = serializers.IntegerField()
    total_clientes = serializers.IntegerField()
    clientes_activos = serializers.IntegerField()
    tipos_comprobante_disponibles = serializers.IntegerField()

# ===========================================
# SERIALIZERS PARA IMPORTACIÓN/EXPORTACIÓN
# ===========================================

class ImportarClientesSerializer(serializers.Serializer):
    """Serializer para importar clientes desde Excel/CSV"""
    
    archivo = serializers.FileField()
    empresa = serializers.PrimaryKeyRelatedField(queryset=Empresa.objects.filter(activo=True))
    sobrescribir_existentes = serializers.BooleanField(default=False)
    
    def validate_archivo(self, value):
        """Validar tipo de archivo"""
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                "Solo se permiten archivos Excel (.xlsx, .xls) o CSV (.csv)"
            )
        
        # Validar tamaño (máximo 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("El archivo no debe superar los 5MB")
        
        return value

class ExportarClientesSerializer(serializers.Serializer):
    """Serializer para exportar clientes"""
    
    empresa = serializers.PrimaryKeyRelatedField(
        queryset=Empresa.objects.filter(activo=True),
        required=False
    )
    formato = serializers.ChoiceField(choices=[
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ], default='xlsx')
    incluir_inactivos = serializers.BooleanField(default=False)
    tipo_documento = serializers.ChoiceField(
        choices=[('todos', 'Todos')] + Cliente.TIPOS_DOCUMENTO,
        default='todos',
        required=False
    )