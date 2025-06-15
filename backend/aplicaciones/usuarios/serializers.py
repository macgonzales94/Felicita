"""
FELICITA - Serializers Usuarios
Sistema de Facturación Electrónica para Perú
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Usuario, SesionUsuario, LogAuditoria
import logging

logger = logging.getLogger('felicita.usuarios')

class LoginSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para login con JWT"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información del usuario
        data['usuario'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nombre_completo': self.user.nombre_completo,
            'rol': self.user.rol,
            'empresa_id': self.user.empresa_id,
            'empresa_nombre': self.user.empresa.razon_social if self.user.empresa else None,
            'permisos': self.user.obtener_permisos_rol(),
        }
        
        return data

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para Usuario"""
    
    nombre_completo = serializers.CharField(read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    puede_acceder = serializers.BooleanField(read_only=True)
    esta_bloqueado = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'rol', 'telefono', 'documento_identidad',
            'empresa', 'empresa_nombre', 'sucursales', 'is_active',
            'puede_acceder', 'esta_bloqueado', 'ultimo_acceso_ip',
            'last_login', 'date_joined'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        sucursales = validated_data.pop('sucursales', [])
        
        usuario = Usuario.objects.create_user(**validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        
        if sucursales:
            usuario.sucursales.set(sucursales)
        
        return usuario

class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    
    password_actual = serializers.CharField(write_only=True)
    password_nuevo = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirmacion = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['password_nuevo'] != attrs['password_confirmacion']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
    def validate_password_actual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña actual incorrecta")
        return value