"""
URLs para autenticación y gestión de usuarios en FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    IniciarSesionView, RegistroUsuarioView, CerrarSesionView,
    PerfilUsuarioView, CambiarPasswordView, UsuarioViewSet,
    SesionUsuarioViewSet, LogActividadViewSet, EstadisticasUsuariosView,
    verificar_token, verificar_disponibilidad_username, verificar_disponibilidad_email
)

app_name = 'usuarios'

# Router para ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'sesiones', SesionUsuarioViewSet, basename='sesion')
router.register(r'actividades', LogActividadViewSet, basename='actividad')

urlpatterns = [
    # ==============================================
    # AUTENTICACIÓN JWT
    # ==============================================
    
    # Inicio de sesión personalizado
    path('login/', IniciarSesionView.as_view(), name='login'),
    
    # Registro de usuarios
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    
    # Cerrar sesión
    path('logout/', CerrarSesionView.as_view(), name='logout'),
    
    # Tokens JWT estándar
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # ==============================================
    # GESTIÓN DE PERFIL
    # ==============================================
    
    # Perfil del usuario actual
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    
    # Cambiar contraseña
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    
    # ==============================================
    # VALIDACIONES Y VERIFICACIONES
    # ==============================================
    
    # Verificar si token es válido
    path('verificar-token/', verificar_token, name='verificar_token'),
    
    # Verificar disponibilidad de username
    path('verificar-username/', verificar_disponibilidad_username, name='verificar_username'),
    
    # Verificar disponibilidad de email
    path('verificar-email/', verificar_disponibilidad_email, name='verificar_email'),
    
    # ==============================================
    # ESTADÍSTICAS Y REPORTES
    # ==============================================
    
    # Estadísticas de usuarios (solo administradores)
    path('estadisticas/', EstadisticasUsuariosView.as_view(), name='estadisticas'),
    
    # ==============================================
    # VIEWSETS (CRUD completo)
    # ==============================================
    
    # URLs del router (usuarios, sesiones, actividades)
    path('', include(router.urls)),
]

"""
==============================================
ENDPOINTS DISPONIBLES:
==============================================

AUTENTICACIÓN:
POST   /api/auth/login/              # Iniciar sesión
POST   /api/auth/registro/           # Registrar usuario  
POST   /api/auth/logout/             # Cerrar sesión
POST   /api/auth/refresh/            # Renovar token
POST   /api/auth/verify/             # Verificar token
GET    /api/auth/verificar-token/    # Verificar token custom

GESTIÓN DE PERFIL:
GET    /api/auth/perfil/             # Obtener perfil
PUT    /api/auth/perfil/             # Actualizar perfil
POST   /api/auth/cambiar-password/   # Cambiar contraseña

VALIDACIONES:
GET    /api/auth/verificar-username/ # Verificar disponibilidad username
GET    /api/auth/verificar-email/    # Verificar disponibilidad email

ADMINISTRACIÓN DE USUARIOS (Solo Admin):
GET    /api/auth/usuarios/           # Listar usuarios
POST   /api/auth/usuarios/           # Crear usuario
GET    /api/auth/usuarios/{id}/      # Obtener usuario específico
PUT    /api/auth/usuarios/{id}/      # Actualizar usuario
PATCH  /api/auth/usuarios/{id}/      # Actualizar parcialmente usuario
DELETE /api/auth/usuarios/{id}/      # Eliminar usuario

ACCIONES ESPECIALES USUARIOS:
POST   /api/auth/usuarios/{id}/activar/        # Activar usuario
POST   /api/auth/usuarios/{id}/desactivar/     # Desactivar usuario
POST   /api/auth/usuarios/{id}/resetear-password/  # Resetear contraseña

GESTIÓN DE SESIONES:
GET    /api/auth/sesiones/                      # Listar sesiones
GET    /api/auth/sesiones/{id}/                 # Obtener sesión específica
GET    /api/auth/sesiones/mis-sesiones/         # Mis sesiones del usuario actual
POST   /api/auth/sesiones/{id}/cerrar-sesion/   # Cerrar sesión específica

LOGS DE ACTIVIDAD:
GET    /api/auth/actividades/                   # Listar actividades
GET    /api/auth/actividades/{id}/              # Actividad específica
GET    /api/auth/actividades/mis-actividades/   # Mis actividades del usuario actual

ESTADÍSTICAS Y MONITOREO:
GET    /api/auth/estadisticas/                  # Estadísticas de usuarios y seguridad

==============================================
FILTROS DISPONIBLES:
==============================================

Usuarios:
- ?rol=ADMINISTRADOR,CONTADOR,VENDEDOR,CLIENTE
- ?is_active=true,false
- ?empresa={id}
- ?search={término}

Sesiones:
- ?activa=true,false
- ?usuario={id}
- ?direccion_ip={ip}

Actividades:
- ?usuario={id}
- ?accion={accion}
- ?modulo={modulo}
- ?fecha_creacion__gte={fecha}
- ?search={término}

==============================================
PERMISOS POR ROL:
==============================================

ADMINISTRADOR:
- Acceso completo a todos los endpoints
- Puede gestionar todos los usuarios
- Puede ver todas las sesiones y actividades

CONTADOR:
- Solo puede ver su propio perfil
- Puede ver sus propias sesiones y actividades
- No puede gestionar otros usuarios

VENDEDOR:
- Solo puede ver su propio perfil
- Puede ver sus propias sesiones y actividades
- No puede gestionar otros usuarios

CLIENTE:
- Solo puede ver su propio perfil
- Puede ver sus propias sesiones
- Acceso muy limitado al sistema

==============================================
RATE LIMITING:
==============================================

- Login: 5 intentos por minuto por IP
- API General: 100 requests por minuto por usuario autenticado
- API Anónima: 30 requests por minuto por IP
- Verificaciones: Sin límite especial (usan límite general)

==============================================
HEADERS REQUERIDOS:
==============================================

Autenticación:
Authorization: Bearer {access_token}

Content-Type:
Content-Type: application/json

CORS habilitado para:
- http://localhost:3000
- http://127.0.0.1:3000
- http://localhost:5173
"""