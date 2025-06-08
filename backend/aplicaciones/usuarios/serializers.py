"""
SERIALIZERS USUARIOS - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Serializers para autenticación, usuarios, roles y permisos
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

from .models import (
    Usuario, Rol, PermisoPersonalizado, UsuarioRol,
    SesionUsuario, LogActividadUsuario
)


# =============================================================================
# SERIALIZERS BASE
# =============================================================================
class BaseSerializer(serializers.ModelSerializer):
    """
    Serializer base con funcionalidades comunes
    """
    
    def validate_email(self, value):
        """Validar formato de email"""
        if value:
            value = value.lower().strip()
        return value


# =============================================================================
# SERIALIZERS DE USUARIO
# =============================================================================
class UsuarioSerializer(BaseSerializer):
    """
    Serializer principal para usuarios
    """
    password = serializers.CharField(write_only=True, required=False)
    confirmar_password = serializers.CharField(write_only=True, required=False)
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    roles_nombres = serializers.SerializerMethodField()
    permisos = serializers.SerializerMethodField()
    foto_perfil_url = serializers.SerializerMethodField()
    esta_activo = serializers.BooleanField(source='is_active', read_only=True)
    ultimo_login = serializers.DateTimeField(source='fecha_ultimo_login', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombres', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'telefono', 'cargo',
            'departamento', 'fecha_ingreso', 'fecha_nacimiento', 'genero',
            'direccion', 'distrito', 'provincia', 'departamento_ubigeo',
            'foto_perfil', 'foto_perfil_url', 'esta_activo', 'ultimo_login',
            'requiere_cambio_password', 'configuracion_notificaciones',
            'empresa_nombre', 'roles_nombres', 'permisos',
            'password', 'confirmar_password', 'creado_en', 'actualizado_en'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'fecha_ingreso': {'required': False},
            'creado_en': {'read_only': True},
            'actualizado_en': {'read_only': True}
        }
    
    def get_roles_nombres(self, obj):
        """Obtener nombres de roles del usuario"""
        return [ur.rol.nombre for ur in obj.usuario_roles.filter(activo=True)]
    
    def get_permisos(self, obj):
        """Obtener permisos del usuario"""
        permisos = set()
        
        # Permisos por roles
        for usuario_rol in obj.usuario_roles.filter(activo=True):
            for permiso in usuario_rol.rol.permisos.all():
                permisos.add(permiso.nombre)
        
        # Permisos personalizados
        for permiso in obj.permisos_personalizados.all():
            permisos.add(permiso.nombre)
        
        return list(permisos)
    
    def get_foto_perfil_url(self, obj):
        """Obtener URL de foto de perfil"""
        if obj.foto_perfil:
            return obj.foto_perfil.url
        return None
    
    def validate(self, attrs):
        """Validaciones del usuario"""
        # Validar contraseña si se proporciona
        if 'password' in attrs:
            password = attrs['password']
            confirmar_password = attrs.get('confirmar_password')
            
            if password != confirmar_password:
                raise serializers.ValidationError(
                    "Las contraseñas no coinciden"
                )
            
            try:
                validate_password(password)
            except ValidationError as e:
                raise serializers.ValidationError(
                    {"password": list(e.messages)}
                )
        
        # Validar número de documento único
        numero_documento = attrs.get('numero_documento')
        if numero_documento and self.instance:
            # Al actualizar, excluir el usuario actual
            if Usuario.objects.exclude(id=self.instance.id).filter(
                numero_documento=numero_documento
            ).exists():
                raise serializers.ValidationError(
                    "Ya existe un usuario con este número de documento"
                )
        elif numero_documento:
            # Al crear, verificar que no exista
            if Usuario.objects.filter(numero_documento=numero_documento).exists():
                raise serializers.ValidationError(
                    "Ya existe un usuario con este número de documento"
                )
        
        return attrs
    
    def create(self, validated_data):
        """Crear usuario"""
        password = validated_data.pop('password', None)
        validated_data.pop('confirmar_password', None)
        
        usuario = Usuario.objects.create_user(**validated_data)
        
        if password:
            usuario.set_password(password)
            usuario.save()
        
        return usuario
    
    def update(self, instance, validated_data):
        """Actualizar usuario"""
        password = validated_data.pop('password', None)
        validated_data.pop('confirmar_password', None)
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar contraseña si se proporciona
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UsuarioResumenSerializer(BaseSerializer):
    """
    Serializer resumido para listados de usuarios
    """
    nombre_completo = serializers.SerializerMethodField()
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    roles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombres', 'apellido_paterno', 'apellido_materno',
            'nombre_completo', 'cargo', 'is_active', 'fecha_ultimo_login',
            'empresa_nombre', 'roles_count', 'creado_en'
        ]
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo"""
        return f"{obj.nombres} {obj.apellido_paterno} {obj.apellido_materno}".strip()
    
    def get_roles_count(self, obj):
        """Obtener cantidad de roles activos"""
        return obj.usuario_roles.filter(activo=True).count()


class UsuarioCreateSerializer(BaseSerializer):
    """
    Serializer para crear usuarios
    """
    password = serializers.CharField(write_only=True)
    confirmar_password = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Lista de IDs de roles a asignar"
    )
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'nombres', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'telefono', 'cargo',
            'departamento', 'fecha_ingreso', 'password', 'confirmar_password',
            'roles'
        ]
    
    def validate(self, attrs):
        """Validaciones para crear usuario"""
        # Validar contraseñas
        password = attrs['password']
        confirmar_password = attrs['confirmar_password']
        
        if password != confirmar_password:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        # Validar email único
        email = attrs['email'].lower().strip()
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email")
        
        return attrs
    
    def create(self, validated_data):
        """Crear usuario con roles"""
        roles_ids = validated_data.pop('roles', [])
        validated_data.pop('confirmar_password')
        
        # Crear usuario
        usuario = Usuario.objects.create_user(**validated_data)
        
        # Asignar roles
        for rol_id in roles_ids:
            try:
                rol = Rol.objects.get(id=rol_id)
                UsuarioRol.objects.create(
                    usuario=usuario,
                    rol=rol,
                    asignado_por=self.context['request'].user
                )
            except Rol.DoesNotExist:
                continue
        
        return usuario


class PerfilUsuarioSerializer(BaseSerializer):
    """
    Serializer para perfil del usuario autenticado
    """
    nombre_completo = serializers.SerializerMethodField()
    empresa_info = serializers.SerializerMethodField()
    roles_activos = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombres', 'apellido_paterno', 'apellido_materno',
            'nombre_completo', 'tipo_documento', 'numero_documento', 'telefono',
            'cargo', 'departamento', 'fecha_ingreso', 'fecha_nacimiento',
            'genero', 'direccion', 'distrito', 'provincia', 'departamento_ubigeo',
            'foto_perfil', 'configuracion_notificaciones', 'empresa_info',
            'roles_activos', 'fecha_ultimo_login', 'requiere_cambio_password'
        ]
        read_only_fields = [
            'id', 'email', 'fecha_ingreso', 'empresa_info', 'roles_activos',
            'fecha_ultimo_login', 'requiere_cambio_password'
        ]
    
    def get_nombre_completo(self, obj):
        """Obtener nombre completo"""
        return f"{obj.nombres} {obj.apellido_paterno} {obj.apellido_materno}".strip()
    
    def get_empresa_info(self, obj):
        """Obtener información de la empresa"""
        if obj.empresa:
            return {
                'id': obj.empresa.id,
                'razon_social': obj.empresa.razon_social,
                'ruc': obj.empresa.ruc
            }
        return None
    
    def get_roles_activos(self, obj):
        """Obtener roles activos del usuario"""
        return [
            {
                'id': ur.rol.id,
                'nombre': ur.rol.nombre,
                'descripcion': ur.rol.descripcion,
                'fecha_asignacion': ur.fecha_asignacion
            }
            for ur in obj.usuario_roles.filter(activo=True).select_related('rol')
        ]


# =============================================================================
# SERIALIZERS DE AUTENTICACIÓN
# =============================================================================
class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para login
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover campos por defecto del TokenObtainPairSerializer
        if 'username' in self.fields:
            del self.fields['username']
    
    class Meta:
        fields = ['email', 'password']
    
    def validate(self, attrs):
        """Validar credenciales"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            email = email.lower().strip()
            attrs['email'] = email
            
            # Verificar que el usuario existe
            try:
                usuario = Usuario.objects.get(email=email)
                if not usuario.is_active:
                    raise serializers.ValidationError(
                        'Usuario inactivo'
                    )
            except Usuario.DoesNotExist:
                raise serializers.ValidationError(
                    'Credenciales inválidas'
                )
        
        return attrs


class CambiarPasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar contraseña
    """
    password_actual = serializers.CharField()
    password_nueva = serializers.CharField()
    confirmar_password = serializers.CharField()
    
    def validate(self, attrs):
        """Validar cambio de contraseña"""
        password_nueva = attrs['password_nueva']
        confirmar_password = attrs['confirmar_password']
        
        if password_nueva != confirmar_password:
            raise serializers.ValidationError(
                "Las contraseñas nuevas no coinciden"
            )
        
        # Validar fortaleza de contraseña
        try:
            validate_password(password_nueva)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"password_nueva": list(e.messages)}
            )
        
        return attrs


# =============================================================================
# SERIALIZERS DE ROLES Y PERMISOS
# =============================================================================
class PermisoPersonalizadoSerializer(serializers.ModelSerializer):
    """
    Serializer para permisos personalizados
    """
    
    class Meta:
        model = PermisoPersonalizado
        fields = [
            'id', 'nombre', 'descripcion', 'modulo', 'accion',
            'nivel', 'activo', 'creado_en'
        ]


class RolSerializer(serializers.ModelSerializer):
    """
    Serializer para roles
    """
    permisos = PermisoPersonalizadoSerializer(many=True, read_only=True)
    permisos_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    usuarios_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'descripcion', 'nivel', 'activo',
            'permisos', 'permisos_ids', 'usuarios_count',
            'creado_en', 'actualizado_en'
        ]
    
    def get_usuarios_count(self, obj):
        """Obtener cantidad de usuarios con este rol"""
        return obj.usuario_roles.filter(activo=True).count()
    
    def create(self, validated_data):
        """Crear rol con permisos"""
        permisos_ids = validated_data.pop('permisos_ids', [])
        rol = Rol.objects.create(**validated_data)
        
        # Asignar permisos
        if permisos_ids:
            permisos = PermisoPersonalizado.objects.filter(id__in=permisos_ids)
            rol.permisos.set(permisos)
        
        return rol
    
    def update(self, instance, validated_data):
        """Actualizar rol con permisos"""
        permisos_ids = validated_data.pop('permisos_ids', None)
        
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar permisos si se proporcionan
        if permisos_ids is not None:
            permisos = PermisoPersonalizado.objects.filter(id__in=permisos_ids)
            instance.permisos.set(permisos)
        
        return instance


# =============================================================================
# SERIALIZERS DE SESIONES Y ACTIVIDAD
# =============================================================================
class SesionUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para sesiones de usuario
    """
    usuario_nombre = serializers.CharField(source='usuario.nombres', read_only=True)
    duracion = serializers.SerializerMethodField()
    
    class Meta:
        model = SesionUsuario
        fields = [
            'id', 'usuario_nombre', 'ip_address', 'user_agent',
            'dispositivo', 'navegador', 'fecha_inicio', 'fecha_fin',
            'activa', 'duracion'
        ]
    
    def get_duracion(self, obj):
        """Obtener duración de la sesión"""
        if obj.fecha_fin:
            delta = obj.fecha_fin - obj.fecha_inicio
            return str(delta)
        elif obj.activa:
            delta = timezone.now() - obj.fecha_inicio
            return str(delta)
        return None


class LogActividadUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para log de actividad
    """
    usuario_nombre = serializers.CharField(source='usuario.nombres', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = LogActividadUsuario
        fields = [
            'id', 'usuario_nombre', 'accion', 'modulo', 'descripcion',
            'ip_address', 'user_agent', 'fecha', 'tiempo_transcurrido'
        ]
    
    def get_tiempo_transcurrido(self, obj):
        """Obtener tiempo transcurrido desde la actividad"""
        delta = timezone.now() - obj.fecha
        
        if delta.days > 0:
            return f"hace {delta.days} días"
        elif delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"hace {horas} horas"
        elif delta.seconds > 60:
            minutos = delta.seconds // 60
            return f"hace {minutos} minutos"
        else:
            return "hace unos segundos"


# =============================================================================
# SERIALIZERS PARA ESTADÍSTICAS
# =============================================================================
class EstadisticasUsuarioSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de usuarios
    """
    total_usuarios = serializers.IntegerField()
    usuarios_activos = serializers.IntegerField()
    usuarios_inactivos = serializers.IntegerField()
    nuevos_usuarios_mes = serializers.IntegerField()
    logins_hoy = serializers.IntegerField()
    logins_semana = serializers.IntegerField()
    fecha_consulta = serializers.DateTimeField()


# =============================================================================
# SERIALIZERS DE VALIDACIÓN
# =============================================================================
class ValidarEmailSerializer(serializers.Serializer):
    """
    Serializer para validar email
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validar que el email no esté en uso"""
        if Usuario.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "Este email ya está registrado"
            )
        return value.lower()


class VerificarPermisosSerializer(serializers.Serializer):
    """
    Serializer para verificar permisos
    """
    permisos = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de permisos a verificar"
    )
    modulo = serializers.CharField(required=False)
    accion = serializers.CharField(required=False)