"""
VIEWS USUARIOS - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Views para autenticación, gestión de usuarios y permisos
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Count
from datetime import datetime, timedelta
import logging

from .models import (
    Usuario, Rol, PermisoPersonalizado, UsuarioRol,
    SesionUsuario, LogActividadUsuario
)
from .serializers import (
    UsuarioSerializer, UsuarioResumenSerializer, UsuarioCreateSerializer,
    RolSerializer, PermisoPersonalizadoSerializer,
    LoginSerializer, CambiarPasswordSerializer,
    PerfilUsuarioSerializer, SesionUsuarioSerializer,
    LogActividadUsuarioSerializer
)

logger = logging.getLogger('felicita.usuarios')


# =============================================================================
# VIEWSET BASE PARA USUARIOS
# =============================================================================
class BaseUsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet base con funcionalidades comunes para usuarios
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        """Filtrar por empresa del usuario autenticado"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'empresa'):
            return queryset.filter(empresa=self.request.user.empresa)
        return queryset.none()


# =============================================================================
# AUTENTICACIÓN
# =============================================================================
class LoginView(TokenObtainPairView):
    """
    Vista personalizada para login con JWT
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Login con validaciones adicionales"""
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Buscar usuario
            try:
                usuario = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return Response(
                    {'error': 'Credenciales inválidas'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Verificar si está bloqueado
            if usuario.esta_bloqueado():
                return Response(
                    {'error': 'Usuario bloqueado temporalmente'},
                    status=status.HTTP_423_LOCKED
                )
            
            # Verificar si está activo
            if not usuario.is_active:
                return Response(
                    {'error': 'Usuario inactivo'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Autenticar
            user = authenticate(email=email, password=password)
            if not user:
                # Incrementar intentos fallidos
                usuario.intentos_login_fallidos += 1
                if usuario.intentos_login_fallidos >= 5:
                    usuario.bloquear_usuario(30)  # 30 minutos
                usuario.save()
                
                return Response(
                    {'error': 'Credenciales inválidas'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Login exitoso
            usuario.intentos_login_fallidos = 0
            usuario.fecha_ultimo_login = timezone.now()
            usuario.save()
            
            # Generar tokens
            refresh = RefreshToken.for_user(user)
            
            # Crear sesión
            sesion = SesionUsuario.objects.create(
                usuario=user,
                token_sesion=str(refresh.access_token),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                dispositivo=self.get_device_info(request),
                navegador=self.get_browser_info(request)
            )
            
            # Log de actividad
            LogActividadUsuario.objects.create(
                usuario=user,
                accion='login',
                modulo='autenticacion',
                descripcion=f'Inicio de sesión exitoso desde {sesion.ip_address}',
                ip_address=sesion.ip_address
            )
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UsuarioSerializer(user).data,
                'session_id': str(sesion.id),
                'requires_password_change': user.requiere_cambio_password
            })
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_device_info(self, request):
        """Obtener información del dispositivo"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'Mobile' in user_agent:
            return 'Móvil'
        elif 'Tablet' in user_agent:
            return 'Tablet'
        return 'Escritorio'
    
    def get_browser_info(self, request):
        """Obtener información del navegador"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'Chrome' in user_agent:
            return 'Chrome'
        elif 'Firefox' in user_agent:
            return 'Firefox'
        elif 'Safari' in user_agent:
            return 'Safari'
        elif 'Edge' in user_agent:
            return 'Edge'
        return 'Desconocido'


class LogoutView(APIView):
    """
    Vista para logout
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Cerrar sesión"""
        try:
            # Obtener token de refresh
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Cerrar sesión activa
            try:
                sesion = SesionUsuario.objects.get(
                    usuario=request.user,
                    activa=True
                )
                sesion.cerrar_sesion()
            except SesionUsuario.DoesNotExist:
                pass
            
            # Log de actividad
            LogActividadUsuario.objects.create(
                usuario=request.user,
                accion='logout',
                modulo='autenticacion',
                descripcion='Cierre de sesión',
                ip_address=self.get_client_ip(request)
            )
            
            return Response({'message': 'Sesión cerrada correctamente'})
            
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            return Response(
                {'error': 'Error al cerrar sesión'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CambiarPasswordView(APIView):
    """
    Vista para cambiar contraseña
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Cambiar contraseña del usuario autenticado"""
        serializer = CambiarPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Verificar contraseña actual
            if not user.check_password(serializer.validated_data['password_actual']):
                return Response(
                    {'error': 'Contraseña actual incorrecta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cambiar contraseña
            user.set_password(serializer.validated_data['password_nueva'])
            user.requiere_cambio_password = False
            user.save()
            
            # Log de actividad
            LogActividadUsuario.objects.create(
                usuario=user,
                accion='actualizar',
                modulo='usuarios',
                descripcion='Cambio de contraseña',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({'message': 'Contraseña cambiada correctamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# GESTIÓN DE USUARIOS
# =============================================================================
class UsuarioViewSet(BaseUsuarioViewSet):
    """
    ViewSet para gestión de usuarios
    """
    serializer_class = UsuarioSerializer
    search_fields = ['email', 'nombres', 'apellido_paterno', 'numero_documento']
    ordering_fields = ['email', 'nombres', 'fecha_ingreso', 'creado_en']
    ordering = ['nombres']
    
    def get_queryset(self):
        """Usuarios de la empresa"""
        if hasattr(self.request.user, 'empresa'):
            return Usuario.objects.filter(empresa=self.request.user.empresa)
        return Usuario.objects.none()
    
    def get_serializer_class(self):
        """Usar serializer apropiado según la acción"""
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action == 'list':
            return UsuarioResumenSerializer
        return UsuarioSerializer
    
    def perform_create(self, serializer):
        """Crear usuario con empresa del usuario autenticado"""
        serializer.save(empresa=self.request.user.empresa)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activar usuario"""
        usuario = self.get_object()
        usuario.is_active = True
        usuario.save()
        
        return Response({'message': 'Usuario activado correctamente'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Desactivar usuario"""
        usuario = self.get_object()
        usuario.is_active = False
        usuario.save()
        
        return Response({'message': 'Usuario desactivado correctamente'})


class PerfilUsuarioView(APIView):
    """
    Vista para obtener perfil del usuario autenticado
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener perfil del usuario"""
        serializer = PerfilUsuarioSerializer(request.user)
        return Response(serializer.data)


class ActualizarPerfilView(APIView):
    """
    Vista para actualizar perfil del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        """Actualizar perfil del usuario"""
        serializer = PerfilUsuarioSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# ROLES Y PERMISOS
# =============================================================================
class RolViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de roles
    """
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


class PermisoPersonalizadoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de permisos personalizados
    """
    queryset = PermisoPersonalizado.objects.all()
    serializer_class = PermisoPersonalizadoSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['nombre', 'descripcion', 'modulo']
    ordering = ['modulo', 'nombre']


# =============================================================================
# VALIDACIONES Y VERIFICACIONES
# =============================================================================
class ValidarTokenView(APIView):
    """
    Vista para validar token JWT
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Validar si el token es válido"""
        return Response({
            'valid': True,
            'user': UsuarioResumenSerializer(request.user).data
        })


class VerificarPermisosView(APIView):
    """
    Vista para verificar permisos de usuario
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Verificar si el usuario tiene determinados permisos"""
        permisos_requeridos = request.data.get('permisos', [])
        usuario = request.user
        
        # TODO: Implementar lógica de verificación de permisos
        # basada en roles y permisos personalizados
        
        return Response({
            'tiene_permisos': True,  # Placeholder
            'permisos_usuario': [],
            'permisos_faltantes': []
        })


# =============================================================================
# SESIONES Y ACTIVIDAD
# =============================================================================
class SesionesUsuarioView(APIView):
    """
    Vista para obtener sesiones del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener sesiones activas del usuario"""
        sesiones = SesionUsuario.objects.filter(
            usuario=request.user,
            activa=True
        ).order_by('-fecha_inicio')
        
        serializer = SesionUsuarioSerializer(sesiones, many=True)
        return Response(serializer.data)


class LogActividadView(APIView):
    """
    Vista para obtener log de actividad del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener actividad reciente del usuario"""
        actividad = LogActividadUsuario.objects.filter(
            usuario=request.user
        ).order_by('-fecha')[:50]
        
        serializer = LogActividadUsuarioSerializer(actividad, many=True)
        return Response(serializer.data)


# =============================================================================
# ESTADÍSTICAS
# =============================================================================
class EstadisticasLoginView(APIView):
    """
    Vista para estadísticas de login
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener estadísticas de login"""
        # Solo para administradores
        if not request.user.is_superuser:
            return Response(
                {'error': 'Sin permisos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Estadísticas de los últimos 30 días
        hace_30_dias = timezone.now() - timedelta(days=30)
        
        total_logins = LogActividadUsuario.objects.filter(
            accion='login',
            fecha__gte=hace_30_dias
        ).count()
        
        usuarios_activos = Usuario.objects.filter(
            fecha_ultimo_login__gte=hace_30_dias
        ).count()
        
        return Response({
            'total_logins_30_dias': total_logins,
            'usuarios_activos_30_dias': usuarios_activos,
            'fecha_consulta': timezone.now()
        })


# =============================================================================
# VISTAS ADICIONALES PLACEHOLDER
# =============================================================================
class ResetPasswordView(APIView):
    """Vista para solicitar reset de contraseña"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # TODO: Implementar reset de contraseña por email
        return Response({'message': 'Funcionalidad en desarrollo'})


class ResetPasswordConfirmView(APIView):
    """Vista para confirmar reset de contraseña"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # TODO: Implementar confirmación de reset
        return Response({'message': 'Funcionalidad en desarrollo'})


class ActualizarFotoPerfilView(APIView):
    """Vista para actualizar foto de perfil"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # TODO: Implementar subida de foto
        return Response({'message': 'Funcionalidad en desarrollo'})


class ActivarUsuarioView(APIView):
    """Vista para activar usuario (admin)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        # TODO: Implementar activación de usuario
        return Response({'message': 'Usuario activado'})


class DesactivarUsuarioView(APIView):
    """Vista para desactivar usuario (admin)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        # TODO: Implementar desactivación de usuario
        return Response({'message': 'Usuario desactivado'})


# Placeholder para otras vistas mencionadas en URLs
ResetPasswordAdminView = APIView
RolesUsuarioView = APIView
PermisosUsuarioView = APIView
UsuariosPorRolView = APIView
PermisosRolView = APIView
PermisosPorModuloView = APIView
CerrarSesionView = APIView
ValidarEmailView = APIView
PreferenciasUsuarioView = APIView
NotificacionesUsuarioView = APIView
ConfigurarTwoFactorView = APIView
EstadisticasActividadView = APIView
EstadisticasUsuariosView = APIView