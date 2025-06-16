"""
FELICITA - Views Usuarios
Sistema de Facturación Electrónica para Perú

Views completas para autenticación JWT y gestión de usuarios
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import logout
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from .models import Usuario, SesionUsuario, LogAuditoria
from .serializers import (
    UsuarioSerializer, LoginSerializer, CambiarPasswordSerializer,
    RegistroUsuarioSerializer, PerfilUsuarioSerializer,
    SesionUsuarioSerializer, LogAuditoriaSerializer
)
from .permissions import (
    EsAdministradorOContador, EsAdministrador, PuedeGestionarUsuarios
)
import logging

logger = logging.getLogger('felicita.usuarios')

# ===========================================
# UTILIDADES DE IP Y USER AGENT
# ===========================================

def obtener_ip_cliente(request):
    """Obtener IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def obtener_user_agent(request):
    """Obtener User Agent del cliente"""
    return request.META.get('HTTP_USER_AGENT', '')

# ===========================================
# LOGIN VIEW PERSONALIZADA
# ===========================================

class LoginView(TokenObtainPairView):
    """Vista de login personalizada con JWT"""
    
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        """Login con registro de sesión"""
        ip_address = obtener_ip_cliente(request)
        user_agent = obtener_user_agent(request)
        
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Obtener datos del usuario
                usuario_data = response.data.get('usuario', {})
                usuario_id = usuario_data.get('id')
                
                if usuario_id:
                    usuario = Usuario.objects.get(id=usuario_id)
                    
                    # Registrar sesión activa
                    refresh_token = response.data.get('refresh')
                    if refresh_token:
                        try:
                            token = RefreshToken(refresh_token)
                            SesionUsuario.objects.create(
                                usuario=usuario,
                                token_jti=str(token['jti']),
                                ip_address=ip_address,
                                user_agent=user_agent,
                                fecha_expiracion=timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                            )
                        except Exception as e:
                            logger.warning(f"Error creando sesión: {e}")
                    
                    # Log de auditoría
                    LogAuditoria.objects.create(
                        usuario=usuario,
                        accion='LOGIN',
                        recurso='SISTEMA',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        resultado='EXITOSO'
                    )
                    
                    logger.info(f"Login exitoso: {usuario.username} desde {ip_address}")
            
            return response
            
        except Exception as e:
            # Log de intento fallido
            username = request.data.get('username', 'DESCONOCIDO')
            LogAuditoria.objects.create(
                accion='LOGIN_FALLIDO',
                recurso='SISTEMA',
                ip_address=ip_address,
                user_agent=user_agent,
                datos_adicionales={'username': username, 'error': str(e)},
                resultado='FALLIDO'
            )
            logger.warning(f"Login fallido para {username} desde {ip_address}: {e}")
            raise

# ===========================================
# LOGOUT VIEW
# ===========================================

class LogoutView(APIView):
    """Vista para logout con invalidación de token"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout invalidando refresh token"""
        try:
            refresh_token = request.data.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                
                # Marcar sesión como inactiva
                SesionUsuario.objects.filter(
                    usuario=request.user,
                    token_jti=str(token['jti']),
                    activa=True
                ).update(activa=False)
                
                # Blacklist token
                token.blacklist()
            
            # Log de auditoría
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='LOGOUT',
                recurso='SISTEMA',
                ip_address=obtener_ip_cliente(request),
                user_agent=obtener_user_agent(request),
                resultado='EXITOSO'
            )
            
            logger.info(f"Logout exitoso: {request.user.username}")
            return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
            
        except TokenError:
            return Response(
                {'error': 'Token inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            return Response(
                {'error': 'Error interno'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ===========================================
# REGISTRO VIEW
# ===========================================

class RegistroView(APIView):
    """Vista para registro de nuevos usuarios"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Registrar nuevo usuario"""
        serializer = RegistroUsuarioSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.save()
            
            # Log de auditoría
            LogAuditoria.objects.create(
                accion='REGISTRO',
                recurso='USUARIO',
                ip_address=obtener_ip_cliente(request),
                user_agent=obtener_user_agent(request),
                datos_adicionales={'username': usuario.username},
                resultado='EXITOSO'
            )
            
            return Response({
                'message': 'Usuario registrado exitosamente. Pendiente de activación.',
                'usuario_id': usuario.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===========================================
# VIEWSET USUARIO PRINCIPAL
# ===========================================

class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gestión de usuarios"""
    
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['rol', 'empresa', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'documento_identidad']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [PuedeGestionarUsuarios]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrar usuarios según permisos"""
        user = self.request.user
        
        # Superusuario ve todos
        if user.is_superuser:
            return Usuario.objects.all()
        
        # Administrador ve usuarios de su empresa
        if user.rol == 'administrador':
            return Usuario.objects.filter(empresa=user.empresa)
        
        # Contador ve usuarios de su empresa (solo lectura)
        if user.rol == 'contador':
            return Usuario.objects.filter(empresa=user.empresa)
        
        # Otros roles solo se ven a sí mismos
        return Usuario.objects.filter(id=user.id)
    
    def perform_create(self, serializer):
        """Crear usuario con log de auditoría"""
        usuario = serializer.save()
        
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_USUARIO',
            recurso='USUARIO',
            ip_address=obtener_ip_cliente(self.request),
            user_agent=obtener_user_agent(self.request),
            datos_adicionales={'usuario_creado': usuario.username},
            resultado='EXITOSO'
        )
    
    def perform_update(self, serializer):
        """Actualizar usuario con log de auditoría"""
        usuario = serializer.save()
        
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_USUARIO',
            recurso='USUARIO',
            ip_address=obtener_ip_cliente(self.request),
            user_agent=obtener_user_agent(self.request),
            datos_adicionales={'usuario_actualizado': usuario.username},
            resultado='EXITOSO'
        )
    
    def perform_destroy(self, instance):
        """Eliminar usuario (soft delete) con log de auditoría"""
        instance.is_active = False
        instance.save()
        
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR_USUARIO',
            recurso='USUARIO',
            ip_address=obtener_ip_cliente(self.request),
            user_agent=obtener_user_agent(self.request),
            datos_adicionales={'usuario_eliminado': instance.username},
            resultado='EXITOSO'
        )
    
    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Obtener perfil del usuario autenticado"""
        serializer = PerfilUsuarioSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def cambiar_password(self, request):
        """Cambiar contraseña del usuario autenticado"""
        serializer = CambiarPasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['password_nuevo'])
            request.user.save()
            
            # Invalidar todas las sesiones del usuario
            SesionUsuario.objects.filter(
                usuario=request.user,
                activa=True
            ).update(activa=False)
            
            # Log de auditoría
            LogAuditoria.objects.create(
                usuario=request.user,
                accion='CAMBIAR_PASSWORD',
                recurso='USUARIO',
                ip_address=obtener_ip_cliente(request),
                user_agent=obtener_user_agent(request),
                resultado='EXITOSO'
            )
            
            return Response({
                'message': 'Contraseña cambiada correctamente. Inicie sesión nuevamente.'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[EsAdministrador])
    def activar(self, request, pk=None):
        """Activar usuario"""
        usuario = self.get_object()
        usuario.is_active = True
        usuario.save()
        
        LogAuditoria.objects.create(
            usuario=request.user,
            accion='ACTIVAR_USUARIO',
            recurso='USUARIO',
            ip_address=obtener_ip_cliente(request),
            user_agent=obtener_user_agent(request),
            datos_adicionales={'usuario_activado': usuario.username},
            resultado='EXITOSO'
        )
        
        return Response({'message': 'Usuario activado correctamente'})
    
    @action(detail=True, methods=['post'], permission_classes=[EsAdministrador])
    def desactivar(self, request, pk=None):
        """Desactivar usuario"""
        usuario = self.get_object()
        
        if usuario == request.user:
            return Response(
                {'error': 'No puede desactivarse a sí mismo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario.is_active = False
        usuario.save()
        
        # Cerrar sesiones activas
        SesionUsuario.objects.filter(
            usuario=usuario,
            activa=True
        ).update(activa=False)
        
        LogAuditoria.objects.create(
            usuario=request.user,
            accion='DESACTIVAR_USUARIO',
            recurso='USUARIO',
            ip_address=obtener_ip_cliente(request),
            user_agent=obtener_user_agent(request),
            datos_adicionales={'usuario_desactivado': usuario.username},
            resultado='EXITOSO'
        )
        
        return Response({'message': 'Usuario desactivado correctamente'})
    
    @action(detail=True, methods=['post'], permission_classes=[EsAdministrador])
    def desbloquear(self, request, pk=None):
        """Desbloquear usuario"""
        usuario = self.get_object()
        usuario.desbloquear()
        
        LogAuditoria.objects.create(
            usuario=request.user,
            accion='DESBLOQUEAR_USUARIO',
            recurso='USUARIO',
            ip_address=obtener_ip_cliente(request),
            user_agent=obtener_user_agent(request),
            datos_adicionales={'usuario_desbloqueado': usuario.username},
            resultado='EXITOSO'
        )
        
        return Response({'message': 'Usuario desbloqueado correctamente'})
    
    @action(detail=False, methods=['get'])
    def sesiones_activas(self, request):
        """Obtener sesiones activas del usuario"""
        sesiones = SesionUsuario.objects.filter(
            usuario=request.user,
            activa=True,
            fecha_expiracion__gt=timezone.now()
        )
        serializer = SesionUsuarioSerializer(sesiones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def cerrar_sesion(self, request):
        """Cerrar sesión específica"""
        token_jti = request.data.get('token_jti')
        
        if not token_jti:
            return Response(
                {'error': 'token_jti requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sesiones_cerradas = SesionUsuario.objects.filter(
            usuario=request.user,
            token_jti=token_jti,
            activa=True
        ).update(activa=False)
        
        if sesiones_cerradas:
            return Response({'message': 'Sesión cerrada correctamente'})
        else:
            return Response(
                {'error': 'Sesión no encontrada o ya cerrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def cerrar_todas_sesiones(self, request):
        """Cerrar todas las sesiones del usuario"""
        SesionUsuario.objects.filter(
            usuario=request.user,
            activa=True
        ).update(activa=False)
        
        LogAuditoria.objects.create(
            usuario=request.user,
            accion='CERRAR_TODAS_SESIONES',
            recurso='USUARIO',
            ip_address=obtener_ip_cliente(request),
            user_agent=obtener_user_agent(request),
            resultado='EXITOSO'
        )
        
        return Response({'message': 'Todas las sesiones han sido cerradas'})

# ===========================================
# VIEWSET LOG AUDITORÍA
# ===========================================

class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consulta de logs de auditoría"""
    
    queryset = LogAuditoria.objects.all()
    serializer_class = LogAuditoriaSerializer
    permission_classes = [EsAdministradorOContador]
    filterset_fields = ['usuario', 'accion', 'recurso', 'resultado']
    search_fields = ['accion', 'recurso', 'ip_address']
    ordering_fields = ['fecha_hora']
    ordering = ['-fecha_hora']
    
    def get_queryset(self):
        """Filtrar logs según permisos"""
        user = self.request.user
        
        # Superusuario ve todos los logs
        if user.is_superuser:
            return LogAuditoria.objects.all()
        
        # Administrador ve logs de su empresa
        if user.rol == 'administrador':
            return LogAuditoria.objects.filter(
                Q(usuario__empresa=user.empresa) | Q(usuario__isnull=True)
            )
        
        # Contador ve logs de su empresa (solo lectura)
        if user.rol == 'contador':
            return LogAuditoria.objects.filter(
                Q(usuario__empresa=user.empresa) | Q(usuario__isnull=True)
            )
        
        # Otros roles no pueden ver logs
        return LogAuditoria.objects.none()

# ===========================================
# VIEW VERIFICAR PERMISOS
# ===========================================

class VerificarPermisosView(APIView):
    """Vista para verificar permisos específicos"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Verificar si el usuario tiene permisos específicos"""
        permisos = request.data.get('permisos', [])
        
        if not isinstance(permisos, list):
            return Response(
                {'error': 'permisos debe ser una lista'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultados = {}
        for permiso in permisos:
            resultados[permiso] = request.user.tiene_permiso(permiso)
        
        return Response({
            'usuario': request.user.username,
            'rol': request.user.rol,
            'permisos': resultados
        })

# ===========================================
# VIEW ESTADÍSTICAS USUARIOS
# ===========================================

class EstadisticasUsuariosView(APIView):
    """Vista para estadísticas de usuarios"""
    
    permission_classes = [EsAdministradorOContador]
    
    def get(self, request):
        """Obtener estadísticas de usuarios"""
        user = request.user
        
        # Filtrar por empresa si no es superusuario
        if user.is_superuser:
            usuarios_base = Usuario.objects.all()
        else:
            usuarios_base = Usuario.objects.filter(empresa=user.empresa)
        
        estadisticas = {
            'total_usuarios': usuarios_base.count(),
            'usuarios_activos': usuarios_base.filter(is_active=True).count(),
            'usuarios_inactivos': usuarios_base.filter(is_active=False).count(),
            'por_rol': {},
            'sesiones_activas': SesionUsuario.objects.filter(
                usuario__in=usuarios_base,
                activa=True,
                fecha_expiracion__gt=timezone.now()
            ).count(),
        }
        
        # Estadísticas por rol
        for rol_code, rol_name in Usuario.ROLES:
            count = usuarios_base.filter(rol=rol_code).count()
            if count > 0:
                estadisticas['por_rol'][rol_name] = count
        
        return Response(estadisticas)