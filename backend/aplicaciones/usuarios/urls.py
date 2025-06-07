"""
URLs USUARIOS - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

URLs para autenticación, gestión de usuarios y permisos
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# =============================================================================
# CONFIGURACIÓN DEL ROUTER
# =============================================================================
router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'roles', views.RolViewSet, basename='rol')
router.register(r'permisos', views.PermisoPersonalizadoViewSet, basename='permiso')

# =============================================================================
# URLs PRINCIPALES
# =============================================================================
urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # =============================================================================
    # AUTENTICACIÓN JWT
    # =============================================================================
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', views.CambiarPasswordView.as_view(), name='change_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('reset-password-confirm/', views.ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    
    # =============================================================================
    # PERFIL DE USUARIO
    # =============================================================================
    path('profile/', views.PerfilUsuarioView.as_view(), name='profile'),
    path('profile/update/', views.ActualizarPerfilView.as_view(), name='update_profile'),
    path('profile/photo/', views.ActualizarFotoPerfilView.as_view(), name='update_photo'),
    
    # =============================================================================
    # GESTIÓN DE USUARIOS (ADMIN)
    # =============================================================================
    path('usuarios/<uuid:pk>/activate/', views.ActivarUsuarioView.as_view(), name='activate_user'),
    path('usuarios/<uuid:pk>/deactivate/', views.DesactivarUsuarioView.as_view(), name='deactivate_user'),
    path('usuarios/<uuid:pk>/reset-password/', views.ResetPasswordAdminView.as_view(), name='admin_reset_password'),
    path('usuarios/<uuid:pk>/roles/', views.RolesUsuarioView.as_view(), name='user_roles'),
    path('usuarios/<uuid:pk>/permisos/', views.PermisosUsuarioView.as_view(), name='user_permissions'),
    
    # =============================================================================
    # ROLES Y PERMISOS
    # =============================================================================
    path('roles/<uuid:pk>/usuarios/', views.UsuariosPorRolView.as_view(), name='role_users'),
    path('roles/<uuid:pk>/permisos/', views.PermisosRolView.as_view(), name='role_permissions'),
    path('permisos/por-modulo/', views.PermisosPorModuloView.as_view(), name='permissions_by_module'),
    
    # =============================================================================
    # SESIONES Y ACTIVIDAD
    # =============================================================================
    path('sessions/', views.SesionesUsuarioView.as_view(), name='user_sessions'),
    path('sessions/<uuid:session_id>/close/', views.CerrarSesionView.as_view(), name='close_session'),
    path('activity-log/', views.LogActividadView.as_view(), name='activity_log'),
    
    # =============================================================================
    # VALIDACIONES Y VERIFICACIONES
    # =============================================================================
    path('validate-token/', views.ValidarTokenView.as_view(), name='validate_token'),
    path('check-permissions/', views.VerificarPermisosView.as_view(), name='check_permissions'),
    path('validate-email/', views.ValidarEmailView.as_view(), name='validate_email'),
    
    # =============================================================================
    # CONFIGURACIÓN DE USUARIO
    # =============================================================================
    path('preferences/', views.PreferenciasUsuarioView.as_view(), name='user_preferences'),
    path('notifications/', views.NotificacionesUsuarioView.as_view(), name='user_notifications'),
    path('two-factor/', views.ConfigurarTwoFactorView.as_view(), name='two_factor'),
    
    # =============================================================================
    # REPORTES Y ESTADÍSTICAS
    # =============================================================================
    path('stats/login/', views.EstadisticasLoginView.as_view(), name='login_stats'),
    path('stats/activity/', views.EstadisticasActividadView.as_view(), name='activity_stats'),
    path('stats/users/', views.EstadisticasUsuariosView.as_view(), name='users_stats'),
]

# =============================================================================
# NAMESPACE DE LA APLICACIÓN
# =============================================================================
app_name = 'usuarios'