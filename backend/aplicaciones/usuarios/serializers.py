"""
Serializers de autenticación para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Usuario, SesionUsuario, LogActividad, RolUsuario


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """
    Serializer para información pública del usuario (sin datos sensibles)
    """
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    nombre_empresa = serializers.CharField(source='empresa.get_nombre_para_mostrar', read_only=True)
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'tipo_documento', 'tipo_documento_display',
            'numero_documento', 'telefono', 'rol', 'avatar',
            'tema_preferido', 'idioma', 'empresa', 'nombre_empresa',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UsuarioDetalladoSerializer(serializers.ModelSerializer):
    """
    Serializer completo del usuario para administradores
    """
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    nombre_empresa = serializers.CharField(source='empresa.get_nombre_para_mostrar', read_only=True)
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    confirmar_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'tipo_documento', 'tipo_documento_display',
            'numero_documento', 'telefono', 'direccion', 'rol', 'avatar',
            'tema_preferido', 'idioma', 'empresa', 'nombre_empresa',
            'permisos_especiales', 'configuraciones',
            'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'password', 'confirmar_password'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirmar_password': {'write_only': True}
        }
    
    def validate(self, datos):
        """Validar datos del usuario"""
        # Validar contraseñas coinciden
        if 'password' in datos and 'confirmar_password' in datos:
            if datos['password'] != datos['confirmar_password']:
                raise serializers.ValidationError({
                    'confirmar_password': 'Las contraseñas no coinciden'
                })
        
        # Validar password si se proporciona
        if 'password' in datos and datos['password']:
            try:
                validate_password(datos['password'])
            except ValidationError as e:
                raise serializers.ValidationError({'password': e.messages})
        
        return datos
    
    def create(self, datos_validados):
        """Crear nuevo usuario"""
        # Remover confirmar_password antes de crear
        datos_validados.pop('confirmar_password', None)
        
        # Extraer password
        password = datos_validados.pop('password', None)
        
        # Crear usuario
        usuario = Usuario.objects.create(**datos_validados)
        
        # Establecer password si se proporciona
        if password:
            usuario.set_password(password)
            usuario.save()
        
        return usuario
    
    def update(self, instancia, datos_validados):
        """Actualizar usuario existente"""
        # Remover confirmar_password antes de actualizar
        datos_validados.pop('confirmar_password', None)
        
        # Extraer password
        password = datos_validados.pop('password', None)
        
        # Actualizar campos normales
        for campo, valor in datos_validados.items():
            setattr(instancia, campo, valor)
        
        # Actualizar password si se proporciona
        if password:
            instancia.set_password(password)
        
        instancia.save()
        return instancia


class IniciarSesionSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para inicio de sesión con JWT
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cambiar nombres de campos a español
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contraseña'
        
        # Mensajes personalizados en español
        self.fields['username'].error_messages = {
            'required': 'El usuario es requerido',
            'blank': 'El usuario no puede estar vacío'
        }
        self.fields['password'].error_messages = {
            'required': 'La contraseña es requerida',
            'blank': 'La contraseña no puede estar vacía'
        }
    
    @classmethod
    def get_token(cls, usuario):
        """Personalizar token JWT con información adicional"""
        token = super().get_token(usuario)
        
        # Agregar información personalizada al token
        token['usuario_id'] = usuario.id
        token['username'] = usuario.username
        token['email'] = usuario.email
        token['nombre_completo'] = usuario.get_full_name()
        token['rol'] = usuario.rol
        token['empresa_id'] = usuario.empresa_id if usuario.empresa else None
        token['empresa_nombre'] = usuario.empresa.get_nombre_para_mostrar() if usuario.empresa else None
        token['es_administrador'] = usuario.es_administrador()
        token['tema_preferido'] = usuario.tema_preferido
        token['idioma'] = usuario.idioma
        
        return token
    
    def validate(self, datos):
        """Validar credenciales y agregar información del usuario"""
        try:
            # Validación base
            datos = super().validate(datos)
            
            # Obtener usuario autenticado
            usuario = authenticate(
                username=self.initial_data['username'],
                password=self.initial_data['password']
            )
            
            if not usuario:
                raise serializers.ValidationError({
                    'detail': 'Credenciales inválidas'
                })
            
            if not usuario.is_active:
                raise serializers.ValidationError({
                    'detail': 'Usuario desactivado'
                })
            
            # Agregar información del usuario a la respuesta
            datos['usuario'] = UsuarioPublicoSerializer(usuario).data
            
            # Registrar inicio de sesión en logs
            LogActividad.registrar_actividad(
                usuario=usuario,
                accion='INICIO_SESION',
                modulo='AUTENTICACION',
                descripcion='Usuario inició sesión correctamente',
                direccion_ip=self.context.get('request').META.get('REMOTE_ADDR', '127.0.0.1')
            )
            
            return datos
            
        except Exception as e:
            # Registrar intento fallido si tenemos el username
            if 'username' in self.initial_data:
                LogActividad.registrar_actividad(
                    usuario=None,
                    accion='INTENTO_INICIO_SESION_FALLIDO',
                    modulo='AUTENTICACION',
                    descripcion=f'Intento fallido de inicio de sesión para: {self.initial_data["username"]}',
                    datos_adicionales={'error': str(e)},
                    direccion_ip=self.context.get('request').META.get('REMOTE_ADDR', '127.0.0.1')
                )
            
            raise serializers.ValidationError({
                'detail': 'Error en las credenciales. Verifique usuario y contraseña.'
            })


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        label='Contraseña'
    )
    confirmar_password = serializers.CharField(
        write_only=True,
        label='Confirmar Contraseña'
    )
    nombre_empresa = serializers.CharField(source='empresa.razon_social', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'tipo_documento', 'numero_documento', 'telefono',
            'password', 'confirmar_password', 'empresa', 'nombre_empresa'
        ]
        extra_kwargs = {
            'username': {'label': 'Usuario'},
            'email': {'label': 'Correo Electrónico'},
            'first_name': {'label': 'Nombres'},
            'last_name': {'label': 'Apellidos'},
            'numero_documento': {'label': 'Número de Documento'},
            'telefono': {'label': 'Teléfono'},
        }
    
    def validate(self, datos):
        """Validar datos de registro"""
        # Verificar que las contraseñas coinciden
        if datos['password'] != datos['confirmar_password']:
            raise serializers.ValidationError({
                'confirmar_password': 'Las contraseñas no coinciden'
            })
        
        # Validar que el username no existe
        if Usuario.objects.filter(username=datos['username']).exists():
            raise serializers.ValidationError({
                'username': 'Este nombre de usuario ya está en uso'
            })
        
        # Validar que el email no existe
        if Usuario.objects.filter(email=datos['email']).exists():
            raise serializers.ValidationError({
                'email': 'Este correo electrónico ya está registrado'
            })
        
        return datos
    
    def create(self, datos_validados):
        """Crear nuevo usuario registrado"""
        # Remover confirmar_password
        datos_validados.pop('confirmar_password')
        
        # Extraer password
        password = datos_validados.pop('password')
        
        # Crear usuario con rol por defecto
        usuario = Usuario.objects.create(
            **datos_validados,
            rol=RolUsuario.VENDEDOR,  # Rol por defecto para nuevos registros
            is_active=True
        )
        
        # Establecer password
        usuario.set_password(password)
        usuario.save()
        
        # Registrar en logs
        LogActividad.registrar_actividad(
            usuario=usuario,
            accion='REGISTRO_USUARIO',
            modulo='AUTENTICACION',
            descripcion='Usuario se registró en el sistema',
            direccion_ip='127.0.0.1'  # Se puede mejorar obteniendo IP real
        )
        
        return usuario


class CambiarPasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña
    """
    password_actual = serializers.CharField(
        write_only=True,
        label='Contraseña Actual'
    )
    password_nueva = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        label='Nueva Contraseña'
    )
    confirmar_password_nueva = serializers.CharField(
        write_only=True,
        label='Confirmar Nueva Contraseña'
    )
    
    def validate(self, datos):
        """Validar cambio de contraseña"""
        usuario = self.context['request'].user
        
        # Verificar contraseña actual
        if not usuario.check_password(datos['password_actual']):
            raise serializers.ValidationError({
                'password_actual': 'La contraseña actual es incorrecta'
            })
        
        # Verificar que las nuevas contraseñas coinciden
        if datos['password_nueva'] != datos['confirmar_password_nueva']:
            raise serializers.ValidationError({
                'confirmar_password_nueva': 'Las contraseñas no coinciden'
            })
        
        # Verificar que la nueva contraseña es diferente
        if usuario.check_password(datos['password_nueva']):
            raise serializers.ValidationError({
                'password_nueva': 'La nueva contraseña debe ser diferente a la actual'
            })
        
        return datos
    
    def save(self):
        """Guardar nueva contraseña"""
        usuario = self.context['request'].user
        usuario.set_password(self.validated_data['password_nueva'])
        usuario.save()
        
        # Registrar en logs
        LogActividad.registrar_actividad(
            usuario=usuario,
            accion='CAMBIO_PASSWORD',
            modulo='AUTENTICACION',
            descripcion='Usuario cambió su contraseña',
            direccion_ip=self.context['request'].META.get('REMOTE_ADDR', '127.0.0.1')
        )
        
        return usuario


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar perfil del usuario
    """
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    nombre_empresa = serializers.CharField(source='empresa.get_nombre_para_mostrar', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'numero_documento', 'telefono', 'direccion',
            'avatar', 'tema_preferido', 'idioma', 'configuraciones',
            'empresa', 'nombre_empresa'
        ]
        read_only_fields = ['id', 'username', 'empresa']
    
    def update(self, instancia, datos_validados):
        """Actualizar perfil del usuario"""
        # Actualizar campos
        for campo, valor in datos_validados.items():
            setattr(instancia, campo, valor)
        
        instancia.save()
        
        # Registrar en logs
        LogActividad.registrar_actividad(
            usuario=instancia,
            accion='ACTUALIZAR_PERFIL',
            modulo='AUTENTICACION',
            descripcion='Usuario actualizó su perfil',
            direccion_ip=self.context['request'].META.get('REMOTE_ADDR', '127.0.0.1')
        )
        
        return instancia


class SesionUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para sesiones de usuario
    """
    nombre_usuario = serializers.CharField(source='usuario.username', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = SesionUsuario
        fields = [
            'id', 'usuario', 'nombre_usuario', 'direccion_ip',
            'user_agent', 'fecha_inicio', 'fecha_ultimo_acceso',
            'activa', 'tiempo_transcurrido'
        ]
        read_only_fields = ['id', 'fecha_inicio', 'fecha_ultimo_acceso']
    
    def get_tiempo_transcurrido(self, obj):
        """Calcular tiempo transcurrido desde el inicio"""
        from django.utils import timezone
        delta = timezone.now() - obj.fecha_inicio
        
        # Formatear tiempo transcurrido
        if delta.days > 0:
            return f"{delta.days} días"
        elif delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"{horas} horas"
        elif delta.seconds > 60:
            minutos = delta.seconds // 60
            return f"{minutos} minutos"
        else:
            return "Menos de 1 minuto"


class LogActividadSerializer(serializers.ModelSerializer):
    """
    Serializer para logs de actividad
    """
    nombre_usuario = serializers.CharField(source='usuario.username', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = LogActividad
        fields = [
            'id', 'usuario', 'nombre_usuario', 'accion', 'modulo',
            'descripcion', 'datos_adicionales', 'direccion_ip',
            'fecha_creacion', 'tiempo_transcurrido'
        ]
        read_only_fields = ['id', 'fecha_creacion']
    
    def get_tiempo_transcurrido(self, obj):
        """Calcular tiempo transcurrido desde la actividad"""
        from django.utils import timezone
        delta = timezone.now() - obj.fecha_creacion
        
        if delta.days > 0:
            return f"Hace {delta.days} días"
        elif delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"Hace {horas} horas"
        elif delta.seconds > 60:
            minutos = delta.seconds // 60
            return f"Hace {minutos} minutos"
        else:
            return "Hace menos de 1 minuto"