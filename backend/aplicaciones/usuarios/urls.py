"""
FELICITA - URLs Usuarios
Sistema de Facturación Electrónica para Perú

URLs completas para autenticación JWT y gestión de usuarios
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import (
    LoginView, LogoutView, RegistroView, UsuarioViewSet, 
    LogAuditoriaViewSet, VerificarPermisosView, EstadisticasUsuariosView
)

# ===========================================
# ROUTER PRINCIPAL
# ===========================================

router = DefaultRouter()

# Registrar ViewSets
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'logs-auditoria', LogAuditoriaViewSet, basename='log-auditoria')

# ===========================================
# PATRONES DE URL
# ===========================================

urlpatterns = [
    # ===========================================
    # AUTENTICACIÓN JWT
    # ===========================================
    
    # Login y obtención de tokens
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    
    # Gestión de tokens JWT
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # ===========================================
    # GESTIÓN DE USUARIOS
    # ===========================================
    
    # ViewSets registrados (incluye todas las acciones CRUD + personalizadas)
    path('', include(router.urls)),
    
    # ===========================================
    # ENDPOINTS ESPECÍFICOS
    # ===========================================
    
    # Verificación de permisos
    path('auth/verificar-permisos/', VerificarPermisosView.as_view(), name='verificar-permisos'),
    
    # Estadísticas
    path('usuarios/estadisticas/', EstadisticasUsuariosView.as_view(), name='estadisticas-usuarios'),
]

# ===========================================
# NOMBRES DE URL GENERADOS POR EL ROUTER
# ===========================================

"""
El router genera automáticamente las siguientes URLs para UsuarioViewSet:

USUARIOS:
- GET    /api/usuarios/usuarios/                    - Lista de usuarios
- POST   /api/usuarios/usuarios/                    - Crear usuario
- GET    /api/usuarios/usuarios/{id}/               - Detalle de usuario
- PUT    /api/usuarios/usuarios/{id}/               - Actualizar usuario completo
- PATCH  /api/usuarios/usuarios/{id}/               - Actualizar usuario parcial
- DELETE /api/usuarios/usuarios/{id}/               - Eliminar usuario (soft delete)

ACCIONES PERSONALIZADAS DE USUARIO:
- GET    /api/usuarios/usuarios/perfil/             - Perfil del usuario autenticado
- POST   /api/usuarios/usuarios/cambiar_password/   - Cambiar contraseña
- POST   /api/usuarios/usuarios/{id}/activar/       - Activar usuario
- POST   /api/usuarios/usuarios/{id}/desactivar/    - Desactivar usuario
- POST   /api/usuarios/usuarios/{id}/desbloquear/   - Desbloquear usuario
- GET    /api/usuarios/usuarios/sesiones_activas/   - Sesiones activas del usuario
- POST   /api/usuarios/usuarios/cerrar_sesion/      - Cerrar sesión específica
- POST   /api/usuarios/usuarios/cerrar_todas_sesiones/ - Cerrar todas las sesiones

LOGS DE AUDITORÍA:
- GET    /api/usuarios/logs-auditoria/              - Lista de logs de auditoría
- GET    /api/usuarios/logs-auditoria/{id}/         - Detalle de log específico

AUTENTICACIÓN:
- POST   /api/usuarios/auth/login/                  - Login con credenciales
- POST   /api/usuarios/auth/logout/                 - Logout e invalidar token
- POST   /api/usuarios/auth/registro/               - Registro de nuevo usuario
- POST   /api/usuarios/auth/token/refresh/          - Renovar access token
- POST   /api/usuarios/auth/token/blacklist/        - Invalidar refresh token

UTILIDADES:
- POST   /api/usuarios/auth/verificar-permisos/     - Verificar permisos específicos
- GET    /api/usuarios/usuarios/estadisticas/       - Estadísticas de usuarios
"""

# ===========================================
# CONFIGURACIÓN DE NOMBRES
# ===========================================

app_name = 'usuarios'

# ===========================================
# DOCUMENTACIÓN DE ENDPOINTS
# ===========================================

"""
DOCUMENTACIÓN DETALLADA DE ENDPOINTS:

1. POST /api/usuarios/auth/login/
   - Descripción: Autenticar usuario y obtener tokens JWT
   - Body: {"username": "usuario", "password": "contraseña"}
   - Response: {
       "access": "access_token",
       "refresh": "refresh_token",
       "usuario": {
         "id": 1,
         "username": "usuario",
         "nombre_completo": "Nombre Usuario",
         "rol": "administrador",
         "empresa_id": 1,
         "permisos": ["core.*", "usuarios.*"]
       }
     }

2. POST /api/usuarios/auth/logout/
   - Descripción: Cerrar sesión e invalidar refresh token
   - Headers: Authorization: Bearer <access_token>
   - Body: {"refresh_token": "refresh_token"}
   - Response: {"message": "Logout exitoso"}

3. GET /api/usuarios/usuarios/perfil/
   - Descripción: Obtener perfil del usuario autenticado
   - Headers: Authorization: Bearer <access_token>
   - Response: {
       "id": 1,
       "username": "usuario",
       "email": "usuario@empresa.com",
       "nombre_completo": "Nombre Usuario",
       "rol": "administrador",
       "permisos": ["core.*"],
       "sucursales_info": [...]
     }

4. POST /api/usuarios/usuarios/cambiar_password/
   - Descripción: Cambiar contraseña del usuario autenticado
   - Headers: Authorization: Bearer <access_token>
   - Body: {
       "password_actual": "contraseña_actual",
       "password_nuevo": "nueva_contraseña",
       "confirmar_password": "nueva_contraseña"
     }
   - Response: {"message": "Contraseña cambiada correctamente"}

5. GET /api/usuarios/usuarios/sesiones_activas/
   - Descripción: Listar sesiones activas del usuario
   - Headers: Authorization: Bearer <access_token>
   - Response: [
       {
         "id": 1,
         "token_jti": "jti_value",
         "ip_address": "192.168.1.1",
         "user_agent": "Mozilla/5.0...",
         "fecha_inicio": "2024-01-01T10:00:00Z",
         "ultima_actividad": "2024-01-01T11:00:00Z"
       }
     ]

6. POST /api/usuarios/auth/verificar-permisos/
   - Descripción: Verificar permisos específicos del usuario
   - Headers: Authorization: Bearer <access_token>
   - Body: {"permisos": ["core.view_empresa", "usuarios.add_usuario"]}
   - Response: {
       "usuario": "admin",
       "rol": "administrador",
       "permisos": {
         "core.view_empresa": true,
         "usuarios.add_usuario": true
       }
     }

7. GET /api/usuarios/usuarios/estadisticas/
   - Descripción: Estadísticas de usuarios (solo admin/contador)
   - Headers: Authorization: Bearer <access_token>
   - Response: {
       "total_usuarios": 10,
       "usuarios_activos": 8,
       "usuarios_inactivos": 2,
       "por_rol": {
         "Administrador": 2,
         "Vendedor": 5,
         "Contador": 1
       },
       "sesiones_activas": 3
     }

CÓDIGOS DE ERROR COMUNES:
- 400: Datos inválidos en el request
- 401: No autenticado (token inválido/expirado)
- 403: Sin permisos para realizar la acción
- 404: Recurso no encontrado
- 429: Demasiadas peticiones (rate limiting)
- 500: Error interno del servidor
"""