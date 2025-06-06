"""
Vistas de autenticación para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout as django_logout
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Usuario, SesionUsuario, LogActividad, RolUsuario
from .serializers import (
    UsuarioPublicoSerializer, UsuarioDetalladoSerializer,
    IniciarSesionSerializer, RegistroUsuarioSerializer,
    CambiarPasswordSerializer, PerfilUsuarioSerializer,
    SesionUsuarioSerializer, LogActividadSerializer
)
from .permissions import (
    EsAdministrador, SoloLeerOPropioUsuario, PermisosEmpresa,
    verificar_permiso_modulo, obtener_queryset_por_empresa
)


class IniciarSesionView(TokenObtainPairView):
    """
    Vista personalizada para inicio de sesión con JWT
    """
    serializer_class = IniciarSesionSerializer
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST'))
    def post(self, request, *args, **kwargs):
        """
        Iniciar sesión con rate limiting
        """
        try:
            # Validar datos de entrada
            serializer = self.get_serializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                # Obtener tokens
                tokens = serializer.validated_data
                
                # Obtener usuario autenticado
                username = request.data.get('username')
                usuario = Usuario.objects.get(username=username)
                
                # Crear o actualizar sesión
                direccion_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                sesion, created = SesionUsuario.objects.get_or_create(
                    usuario=usuario,
                    direccion_ip=direccion_ip,
                    defaults={
                        'token_session': tokens['access'],
                        'user_agent': user_agent,
                        'activa': True
                    }
                )
                
                if not created:
                    # Actualizar sesión existente
                    sesion.token_session = tokens['access']
                    sesion.fecha_ultimo_acceso = timezone.now()
                    sesion.activa = True
                    sesion.save()
                
                # Actualizar último login del usuario
                usuario.last_login = timezone.now()
                usuario.save(update_fields=['last_login'])
                
                return Response({
                    'mensaje': 'Inicio de sesión exitoso',
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                    'usuario': tokens['usuario'],
                    'sesion_id': sesion.id
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'error': 'Credenciales inválidas',
                    'detalles': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Error interno del servidor',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegistroUsuarioView(APIView):
    """
    Vista para registro de nuevos usuarios
    """
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='3/m', method='POST'))
    def post(self, request):
        """
        Registrar nuevo usuario con rate limiting
        """
        try:
            serializer = RegistroUsuarioSerializer(data=request.data)
            
            if serializer.is_valid():
                usuario = serializer.save()
                
                return Response({
                    'mensaje': 'Usuario registrado exitosamente',
                    'usuario': UsuarioPublicoSerializer(usuario).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'error': 'Datos de registro inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Error al registrar usuario',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CerrarSesionView(APIView):
    """
    Vista para cerrar sesión
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Cerrar sesión del usuario actual
        """
        try:
            # Obtener token de refresh si se proporciona
            refresh_token = request.data.get('refresh')
            
            if refresh_token:
                try:
                    # Invalidar token de refresh
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    pass  # Token ya inválido o no válido
            
            # Marcar sesión como inactiva
            direccion_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            try:
                sesion = SesionUsuario.objects.get(
                    usuario=request.user,
                    direccion_ip=direccion_ip,
                    activa=True
                )
                sesion.cerrar_sesion()
            except SesionUsuario.DoesNotExist:
                pass
            
            # Registrar en logs
            LogActividad.registrar_actividad(
                usuario=request.user,
                accion='CERRAR_SESION',
                modulo='AUTENTICACION',
                descripcion='Usuario cerró sesión',
                direccion_ip=direccion_ip
            )
            
            # Cerrar sesión en Django
            django_logout(request)
            
            return Response({
                'mensaje': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al cerrar sesión',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerfilUsuarioView(APIView):
    """
    Vista para gestionar perfil del usuario actual
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Obtener perfil del usuario actual
        """
        try:
            serializer = PerfilUsuarioSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al obtener perfil',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """
        Actualizar perfil del usuario actual
        """
        try:
            serializer = PerfilUsuarioSerializer(
                request.user, 
                data=request.data, 
                context={'request': request}
            )
            
            if serializer.is_valid():
                usuario = serializer.save()
                return Response({
                    'mensaje': 'Perfil actualizado exitosamente',
                    'usuario': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Datos de perfil inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Error al actualizar perfil',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CambiarPasswordView(APIView):
    """
    Vista para cambiar contraseña del usuario actual
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Cambiar contraseña del usuario actual
        """
        try:
            serializer = CambiarPasswordSerializer(
                data=request.data, 
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    'mensaje': 'Contraseña cambiada exitosamente'
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Datos de contraseña inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Error al cambiar contraseña',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios (solo administradores)
    """
    permission_classes = [IsAuthenticated, EsAdministrador]
    
    def get_queryset(self):
        """
        Filtrar usuarios por empresa del administrador
        """
        if self.request.user.is_superuser:
            return Usuario.objects.all()
        
        return obtener_queryset_por_empresa(
            self.request.user, 
            Usuario.objects.all()
        )
    
    def get_serializer_class(self):
        """
        Usar serializer apropiado según la acción
        """
        if self.action in ['list', 'retrieve']:
            return UsuarioDetalladoSerializer
        return UsuarioDetalladoSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Crear nuevo usuario
        """
        try:
            # Asignar empresa del administrador al nuevo usuario
            if not request.user.is_superuser:
                request.data['empresa'] = request.user.empresa.id
            
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                usuario = serializer.save()
                
                # Registrar en logs
                LogActividad.registrar_actividad(
                    usuario=request.user,
                    accion='CREAR_USUARIO',
                    modulo='ADMINISTRACION',
                    descripcion=f'Creó usuario: {usuario.username}',
                    datos_adicionales={'usuario_creado_id': usuario.id},
                    direccion_ip=request.META.get('REMOTE_ADDR', '127.0.0.1')
                )
                
                return Response({
                    'mensaje': 'Usuario creado exitosamente',
                    'usuario': UsuarioDetalladoSerializer(usuario).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'error': 'Datos de usuario inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Error al crear usuario',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Activar usuario
        """
        try:
            usuario = self.get_object()
            usuario.is_active = True
            usuario.save()
            
            LogActividad.registrar_actividad(
                usuario=request.user,
                accion='ACTIVAR_USUARIO',
                modulo='ADMINISTRACION',
                descripcion=f'Activó usuario: {usuario.username}',
                datos_adicionales={'usuario_activado_id': usuario.id},
                direccion_ip=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            
            return Response({
                'mensaje': f'Usuario {usuario.username} activado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al activar usuario',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Desactivar usuario
        """
        try:
            usuario = self.get_object()
            
            # No permitir desactivar el propio usuario
            if usuario == request.user:
                return Response({
                    'error': 'No puede desactivar su propio usuario'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            usuario.is_active = False
            usuario.save()
            
            # Cerrar todas las sesiones activas del usuario
            SesionUsuario.objects.filter(
                usuario=usuario, 
                activa=True
            ).update(activa=False)
            
            LogActividad.registrar_actividad(
                usuario=request.user,
                accion='DESACTIVAR_USUARIO',
                modulo='ADMINISTRACION',
                descripcion=f'Desactivó usuario: {usuario.username}',
                datos_adicionales={'usuario_desactivado_id': usuario.id},
                direccion_ip=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            
            return Response({
                'mensaje': f'Usuario {usuario.username} desactivado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al desactivar usuario',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def resetear_password(self, request, pk=None):
        """
        Resetear contraseña de usuario
        """
        try:
            usuario = self.get_object()
            nueva_password = request.data.get('nueva_password', 'temporal123')
            
            usuario.set_password(nueva_password)
            usuario.save()
            
            LogActividad.registrar_actividad(
                usuario=request.user,
                accion='RESETEAR_PASSWORD',
                modulo='ADMINISTRACION',
                descripcion=f'Reseteó contraseña de usuario: {usuario.username}',
                datos_adicionales={'usuario_reseteado_id': usuario.id},
                direccion_ip=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            
            return Response({
                'mensaje': f'Contraseña reseteada para {usuario.username}',
                'nueva_password': nueva_password
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al resetear contraseña',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SesionUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar sesiones de usuario
    """
    serializer_class = SesionUsuarioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrar sesiones según permisos
        """
        if self.request.user.es_administrador():
            # Administradores ven todas las sesiones de su empresa
            return SesionUsuario.objects.filter(
                usuario__empresa=self.request.user.empresa
            ).order_by('-fecha_ultimo_acceso')
        else:
            # Usuarios normales solo ven sus propias sesiones
            return SesionUsuario.objects.filter(
                usuario=self.request.user
            ).order_by('-fecha_ultimo_acceso')
    
    @action(detail=False, methods=['get'])
    def mis_sesiones(self, request):
        """
        Obtener sesiones del usuario actual
        """
        try:
            sesiones = SesionUsuario.objects.filter(
                usuario=request.user
            ).order_by('-fecha_ultimo_acceso')
            
            serializer = self.get_serializer(sesiones, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al obtener sesiones',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def cerrar_sesion(self, request, pk=None):
        """
        Cerrar sesión específica
        """
        try:
            sesion = self.get_object()
            
            # Solo permitir cerrar propias sesiones o ser administrador
            if sesion.usuario != request.user and not request.user.es_administrador():
                return Response({
                    'error': 'No tiene permisos para cerrar esta sesión'
                }, status=status.HTTP_403_FORBIDDEN)
            
            sesion.cerrar_sesion()
            
            LogActividad.registrar_actividad(
                usuario=request.user,
                accion='CERRAR_SESION_EXTERNA',
                modulo='ADMINISTRACION',
                descripcion=f'Cerró sesión de {sesion.usuario.username}',
                datos_adicionales={'sesion_id': sesion.id},
                direccion_ip=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            
            return Response({
                'mensaje': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al cerrar sesión',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogActividadViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar logs de actividad
    """
    serializer_class = LogActividadSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['usuario', 'accion', 'modulo']
    search_fields = ['descripcion', 'usuario__username']
    ordering_fields = ['fecha_creacion']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """
        Filtrar logs según permisos
        """
        if self.request.user.es_administrador():
            # Administradores ven todos los logs de su empresa
            return LogActividad.objects.filter(
                usuario__empresa=self.request.user.empresa
            )
        else:
            # Usuarios normales solo ven sus propios logs
            return LogActividad.objects.filter(
                usuario=self.request.user
            )
    
    @action(detail=False, methods=['get'])
    def mis_actividades(self, request):
        """
        Obtener actividades del usuario actual
        """
        try:
            actividades = LogActividad.objects.filter(
                usuario=request.user
            ).order_by('-fecha_creacion')[:50]  # Últimas 50 actividades
            
            serializer = self.get_serializer(actividades, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al obtener actividades',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstadisticasUsuariosView(APIView):
    """
    Vista para estadísticas de usuarios (solo administradores)
    """
    permission_classes = [IsAuthenticated, EsAdministrador]
    
    def get(self, request):
        """
        Obtener estadísticas de usuarios
        """
        try:
            empresa = request.user.empresa
            
            # Estadísticas básicas
            total_usuarios = Usuario.objects.filter(empresa=empresa).count()
            usuarios_activos = Usuario.objects.filter(empresa=empresa, is_active=True).count()
            usuarios_inactivos = total_usuarios - usuarios_activos
            
            # Usuarios por rol
            usuarios_por_rol = Usuario.objects.filter(empresa=empresa).values('rol').annotate(
                cantidad=Count('id')
            )
            
            # Sesiones activas
            sesiones_activas = SesionUsuario.objects.filter(
                usuario__empresa=empresa,
                activa=True
            ).count()
            
            # Últimas actividades
            ultimas_actividades = LogActividad.objects.filter(
                usuario__empresa=empresa
            ).order_by('-fecha_creacion')[:10]
            
            return Response({
                'total_usuarios': total_usuarios,
                'usuarios_activos': usuarios_activos,
                'usuarios_inactivos': usuarios_inactivos,
                'usuarios_por_rol': list(usuarios_por_rol),
                'sesiones_activas': sesiones_activas,
                'ultimas_actividades': LogActividadSerializer(ultimas_actividades, many=True).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al obtener estadísticas',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_token(request):
    """
    Vista para verificar si el token JWT es válido
    """
    try:
        return Response({
            'valido': True,
            'usuario': UsuarioPublicoSerializer(request.user).data,
            'mensaje': 'Token válido'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'valido': False,
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def verificar_disponibilidad_username(request):
    """
    Verificar si un username está disponible
    """
    try:
        username = request.GET.get('username', '').strip()
        
        if not username:
            return Response({
                'error': 'Username requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        disponible = not Usuario.objects.filter(username=username).exists()
        
        return Response({
            'disponible': disponible,
            'username': username
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error al verificar disponibilidad',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def verificar_disponibilidad_email(request):
    """
    Verificar si un email está disponible
    """
    try:
        email = request.GET.get('email', '').strip()
        
        if not email:
            return Response({
                'error': 'Email requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        disponible = not Usuario.objects.filter(email=email).exists()
        
        return Response({
            'disponible': disponible,
            'email': email
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Error al verificar disponibilidad',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)