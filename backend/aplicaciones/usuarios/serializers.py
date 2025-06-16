"""
FELICITA - Serializers Usuarios
Sistema de Facturación Electrónica para Perú

Serializers completos para autenticación JWT y gestión de usuarios
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from .models import Usuario, SesionUsuario, LogAuditoria
import logging

logger = logging.getLogger('felicita.usuarios')

# ===========================================
# SERIALIZER LOGIN PERSONALIZADO
# ===========================================

class LoginSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para login con JWT"""
    
    def validate(self, attrs):
        # Obtener usuario antes de validar
        username = attrs.get('username')
        password = attrs.get('password')
        
        try:
            usuario = Usuario.objects.get(username=username)
            
            # Verificar si está bloqueado
            if usuario.esta_bloqueado:
                logger.warning(f"Intento acceso usuario bloqueado: {username}")
                raise serializers.ValidationError(
                    'Usuario bloqueado temporalmente. Inténtelo más tarde.'
                )
            
            # Verificar si está activo
            if not usuario.is_active:
                logger.warning(f"Intento acceso usuario inactivo: {username}")
                raise serializers.ValidationError('Usuario inactivo')
                
        except Usuario.DoesNotExist:
            logger.warning(f"Intento acceso usuario inexistente: {username}")
            raise serializers.ValidationError('Credenciales inválidas')
        
        # Validar credenciales
        try:
            data = super().validate(attrs)
        except Exception as e:
            # Registrar intento fallido
            if 'usuario' in locals():
                usuario.registrar_intento_fallido()
            logger.warning(f"Credenciales inválidas para: {username}")
            raise serializers.ValidationError('Credenciales inválidas')
        
        # Registrar acceso exitoso
        usuario.registrar_acceso()
        
        # Agregar información del usuario al response
        data['usuario'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nombre_completo': self.user.nombre_completo,
            'rol': self.user.rol,
            'empresa_id': self.user.empresa_id,
            'empresa_nombre': self.user.empresa.razon_social if self.user.empresa else None,
            'permisos': self.user.obtener_permisos_rol(),
            'sucursales': [s.id for s in self.user.sucursales.all()],
            'is_superuser': self.user.is_superuser,
            'last_login': self.user.last_login.isoformat() if self.user.last_login else None,
        }
        
        logger.info(f"Login exitoso: {self.user.username} - Rol: {self.user.rol}")
        return data

# ===========================================
# SERIALIZER USUARIO PRINCIPAL
# ===========================================

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para Usuario con validaciones completas"""
    
    nombre_completo = serializers.CharField(read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    puede_acceder = serializers.BooleanField(read_only=True)
    esta_bloqueado = serializers.BooleanField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    confirmar_password = serializers.CharField(write_only=True, required=False)
    sucursales_nombres = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'rol', 'telefono', 'documento_identidad',
            'empresa', 'empresa_nombre', 'sucursales', 'sucursales_nombres',
            'is_active', 'puede_acceder', 'esta_bloqueado', 'ultimo_acceso_ip',
            'last_login', 'date_joined', 'password', 'confirmar_password',
            'notificaciones_email', 'notificaciones_sistema'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'help_text': 'Nombre de usuario único'},
            'email': {'help_text': 'Correo electrónico válido'},
            'rol': {'help_text': 'Rol del usuario en el sistema'},
        }
    
    def get_sucursales_nombres(self, obj):
        """Obtener nombres de sucursales asignadas"""
        return [s.nombre for s in obj.sucursales.all()]
    
    def validate_username(self, value):
        """Validar username único"""
        if self.instance and self.instance.username == value:
            return value
        
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya existe')
        return value
    
    def validate_email(self, value):
        """Validar email único"""
        if self.instance and self.instance.email == value:
            return value
        
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo electrónico ya está registrado')
        return value
    
    def validate_documento_identidad(self, value):
        """Validar documento de identidad"""
        if not value:
            return value
        
        if self.instance and self.instance.documento_identidad == value:
            return value
        
        if Usuario.objects.filter(documento_identidad=value).exists():
            raise serializers.ValidationError('Este documento de identidad ya está registrado')
        
        # Validar formato según tipo
        if len(value) == 8 and value.isdigit():
            # DNI
            return value
        elif len(value) == 11 and value.isdigit():
            # CE o RUC personal
            return value
        else:
            raise serializers.ValidationError(
                'Documento debe ser DNI (8 dígitos) o CE/RUC (11 dígitos)'
            )
    
    def validate(self, attrs):
        """Validaciones globales"""
        password = attrs.get('password')
        confirmar_password = attrs.get('confirmar_password')
        
        # Validar contraseñas si se proporcionan
        if password or confirmar_password:
            if password != confirmar_password:
                raise serializers.ValidationError({
                    'confirmar_password': 'Las contraseñas no coinciden'
                })
            
            if password:
                try:
                    validate_password(password)
                except DjangoValidationError as e:
                    raise serializers.ValidationError({
                        'password': list(e.messages)
                    })
        
        # Validar rol vs empresa
        rol = attrs.get('rol', self.instance.rol if self.instance else None)
        empresa = attrs.get('empresa', self.instance.empresa if self.instance else None)
        
        if rol in ['administrador', 'contador', 'vendedor', 'supervisor'] and not empresa:
            raise serializers.ValidationError({
                'empresa': 'Este rol requiere estar asignado a una empresa'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Crear usuario con contraseña encriptada"""
        password = validated_data.pop('password', None)
        validated_data.pop('confirmar_password', None)
        sucursales = validated_data.pop('sucursales', [])
        
        usuario = Usuario.objects.create(**validated_data)
        
        if password:
            usuario.set_password(password)
            usuario.save()
        
        # Asignar sucursales
        if sucursales:
            usuario.sucursales.set(sucursales)
        
        logger.info(f"Usuario creado: {usuario.username} - Rol: {usuario.rol}")
        return usuario
    
    def update(self, instance, validated_data):
        """Actualizar usuario"""
        password = validated_data.pop('password', None)
        validated_data.pop('confirmar_password', None)
        sucursales = validated_data.pop('sucursales', None)
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar contraseña si se proporciona
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Actualizar sucursales
        if sucursales is not None:
            instance.sucursales.set(sucursales)
        
        logger.info(f"Usuario actualizado: {instance.username}")
        return instance

# ===========================================
# SERIALIZER CAMBIO DE CONTRASEÑA
# ===========================================

class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    
    password_actual = serializers.CharField(required=True)
    password_nuevo = serializers.CharField(required=True)
    confirmar_password = serializers.CharField(required=True)
    
    def validate_password_actual(self, value):
        """Validar contraseña actual"""
        usuario = self.context['request'].user
        if not usuario.check_password(value):
            raise serializers.ValidationError('Contraseña actual incorrecta')
        return value
    
    def validate(self, attrs):
        """Validar que las nuevas contraseñas coincidan"""
        if attrs['password_nuevo'] != attrs['confirmar_password']:
            raise serializers.ValidationError({
                'confirmar_password': 'Las contraseñas no coinciden'
            })
        
        # Validar fortaleza de contraseña
        try:
            validate_password(attrs['password_nuevo'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'password_nuevo': list(e.messages)
            })
        
        return attrs

# ===========================================
# SERIALIZER REGISTRO USUARIO
# ===========================================

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    
    password = serializers.CharField(write_only=True)
    confirmar_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'documento_identidad', 'password', 'confirmar_password'
        ]
    
    def validate(self, attrs):
        """Validaciones de registro"""
        if attrs['password'] != attrs['confirmar_password']:
            raise serializers.ValidationError({
                'confirmar_password': 'Las contraseñas no coinciden'
            })
        
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })
        
        return attrs
    
    def create(self, validated_data):
        """Crear usuario registrado"""
        validated_data.pop('confirmar_password')
        password = validated_data.pop('password')
        
        # Usuario nuevo siempre empieza como cliente
        validated_data['rol'] = 'cliente'
        validated_data['is_active'] = False  # Requiere activación
        
        usuario = Usuario.objects.create(**validated_data)
        usuario.set_password(password)
        usuario.save()
        
        logger.info(f"Usuario registrado: {usuario.username}")
        return usuario

# ===========================================
# SERIALIZER PERFIL USUARIO
# ===========================================

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para perfil del usuario autenticado"""
    
    nombre_completo = serializers.CharField(read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    permisos = serializers.SerializerMethodField()
    sucursales_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'rol', 'telefono', 'documento_identidad',
            'empresa_nombre', 'permisos', 'sucursales_info',
            'notificaciones_email', 'notificaciones_sistema',
            'last_login', 'date_joined'
        ]
        read_only_fields = [
            'id', 'username', 'rol', 'empresa_nombre', 'last_login', 'date_joined'
        ]
    
    def get_permisos(self, obj):
        """Obtener permisos del usuario"""
        return obj.obtener_permisos_rol()
    
    def get_sucursales_info(self, obj):
        """Obtener información de sucursales"""
        return [
            {
                'id': s.id,
                'codigo': s.codigo,
                'nombre': s.nombre,
                'es_principal': s.es_principal
            }
            for s in obj.sucursales.all()
        ]

# ===========================================
# SERIALIZER SESIÓN USUARIO
# ===========================================

class SesionUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para sesiones de usuario"""
    
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    dispositivo_info = serializers.SerializerMethodField()
    
    class Meta:
        model = SesionUsuario
        fields = [
            'id', 'usuario', 'usuario_nombre', 'token_jti', 'ip_address',
            'user_agent', 'dispositivo_info', 'ubicacion', 'activa',
            'fecha_inicio', 'fecha_expiracion', 'ultima_actividad'
        ]
        read_only_fields = ['fecha_inicio', 'ultima_actividad']
    
    def get_dispositivo_info(self, obj):
        """Parsear información del dispositivo"""
        # Aquí puedes usar una librería como user-agents para parsear
        return {
            'navegador': 'Chrome',  # Parsear desde user_agent
            'sistema': 'Windows',   # Parsear desde user_agent
            'dispositivo': 'Desktop' # Determinar tipo
        }

# ===========================================
# SERIALIZER LOG AUDITORÍA
# ===========================================

class LogAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para logs de auditoría"""
    
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = LogAuditoria
        fields = [
            'id', 'usuario', 'usuario_nombre', 'accion', 'recurso',
            'ip_address', 'user_agent', 'datos_adicionales',
            'resultado', 'fecha_hora'
        ]
        read_only_fields = ['fecha_hora']