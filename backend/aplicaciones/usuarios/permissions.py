"""
FELICITA - Permisos Usuarios
Sistema de Facturación Electrónica para Perú

Permisos personalizados para control de acceso granular
"""

from rest_framework import permissions
from django.core.exceptions import PermissionDenied

# ===========================================
# PERMISOS BASE
# ===========================================

class EsAdministrador(permissions.BasePermission):
    """Permiso solo para administradores"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.rol == 'administrador')
        )

class EsAdministradorOContador(permissions.BasePermission):
    """Permiso para administradores y contadores"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.rol in ['administrador', 'contador'])
        )

class EsVendedorOSuperior(permissions.BasePermission):
    """Permiso para vendedores y roles superiores"""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.rol in ['administrador', 'contador', 'vendedor', 'supervisor'])
        )

# ===========================================
# PERMISOS ESPECÍFICOS DE USUARIO
# ===========================================

class PuedeGestionarUsuarios(permissions.BasePermission):
    """Permiso para gestionar usuarios según el rol"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusuario puede todo
        if request.user.is_superuser:
            return True
        
        # Solo administradores pueden gestionar usuarios
        return request.user.rol == 'administrador'
    
    def has_object_permission(self, request, view, obj):
        """Verificar permisos sobre usuario específico"""
        if not request.user.is_authenticated:
            return False
        
        # Superusuario puede todo
        if request.user.is_superuser:
            return True
        
        # Administrador solo puede gestionar usuarios de su empresa
        if request.user.rol == 'administrador':
            # No puede modificar otros administradores o superusuarios
            if obj.is_superuser or (obj.rol == 'administrador' and obj != request.user):
                return False
            return obj.empresa == request.user.empresa
        
        # Solo puede modificar su propio perfil
        return obj == request.user

class PuedeVerUsuarios(permissions.BasePermission):
    """Permiso para ver información de usuarios"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Todos los usuarios autenticados pueden ver algo
        return True
    
    def has_object_permission(self, request, view, obj):
        """Verificar qué usuarios puede ver"""
        if not request.user.is_authenticated:
            return False
        
        # Superusuario ve todos
        if request.user.is_superuser:
            return True
        
        # Administrador y contador ven usuarios de su empresa
        if request.user.rol in ['administrador', 'contador']:
            return obj.empresa == request.user.empresa
        
        # Otros solo se ven a sí mismos
        return obj == request.user

# ===========================================
# PERMISOS DE EMPRESA
# ===========================================

class PerteneceAMismaEmpresa(permissions.BasePermission):
    """Verificar que el usuario pertenece a la misma empresa"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Superusuario puede acceder a cualquier empresa
        if request.user.is_superuser:
            return True
        
        # Verificar que pertenece a la misma empresa
        if hasattr(obj, 'empresa'):
            return obj.empresa == request.user.empresa
        
        return True

class PuedeAccederSucursal(permissions.BasePermission):
    """Verificar acceso a sucursal específica"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Superusuario puede acceder a cualquier sucursal
        if request.user.is_superuser:
            return True
        
        # Verificar acceso a la sucursal
        if hasattr(obj, 'sucursal'):
            return request.user.puede_acceder_sucursal(obj.sucursal)
        
        return True

# ===========================================
# PERMISOS POR MÓDULO
# ===========================================

class PermisoModuloFacturacion(permissions.BasePermission):
    """Permisos para módulo de facturación"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Verificar permisos según método HTTP
        if request.method in permissions.SAFE_METHODS:
            # Lectura
            return request.user.tiene_permiso('facturacion.view_factura')
        else:
            # Escritura
            return request.user.tiene_permiso('facturacion.add_factura')

class PermisoModuloInventario(permissions.BasePermission):
    """Permisos para módulo de inventario"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return request.user.tiene_permiso('inventario.view_producto')
        else:
            return request.user.tiene_permiso('inventario.add_producto')

class PermisoModuloReportes(permissions.BasePermission):
    """Permisos para módulo de reportes"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.tiene_permiso('reportes.view_reporte')

class PermisoModuloContabilidad(permissions.BasePermission):
    """Permisos para módulo de contabilidad"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return request.user.tiene_permiso('contabilidad.view_asiento')
        else:
            return request.user.tiene_permiso('contabilidad.add_asiento')

# ===========================================
# PERMISOS DINÁMICOS
# ===========================================

class PermisoDinamico(permissions.BasePermission):
    """Permiso dinámico basado en string de permiso"""
    
    def __init__(self, permiso_requerido):
        self.permiso_requerido = permiso_requerido
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.tiene_permiso(self.permiso_requerido)

def requiere_permiso(permiso):
    """Decorador para crear permisos dinámicos"""
    class RequierePermiso(permissions.BasePermission):
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            return request.user.tiene_permiso(permiso)
    
    return RequierePermiso

# ===========================================
# PERMISOS COMPUESTOS
# ===========================================

class PermisoLecturaFacturacion(permissions.BasePermission):
    """Permiso específico para lectura de facturación"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Solo métodos de lectura
        if request.method not in permissions.SAFE_METHODS:
            return False
        
        return request.user.rol in ['administrador', 'contador', 'vendedor', 'supervisor']

class PermisoEscrituraFacturacion(permissions.BasePermission):
    """Permiso específico para escritura de facturación"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.rol in ['administrador', 'vendedor', 'supervisor']

# ===========================================
# PERMISOS BASADOS EN HORARIO
# ===========================================

class PermisoHorarioLaboral(permissions.BasePermission):
    """Permiso basado en horario laboral"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusuario siempre puede
        if request.user.is_superuser:
            return True
        
        # Verificar horario (ejemplo: 8:00 - 20:00)
        from datetime import datetime
        hora_actual = datetime.now().hour
        
        if 8 <= hora_actual <= 20:
            return True
        
        # Fuera de horario solo administradores
        return request.user.rol == 'administrador'

# ===========================================
# MIXINS DE PERMISOS
# ===========================================

class PermisosMixin:
    """Mixin para agregar verificación de permisos a ViewSets"""
    
    def verificar_permiso_objeto(self, permiso, obj=None):
        """Verificar permiso sobre objeto específico"""
        if not self.request.user.tiene_permiso(permiso):
            raise PermissionDenied(f"No tiene permisos para: {permiso}")
        
        if obj and hasattr(obj, 'empresa'):
            if not self.request.user.is_superuser:
                if obj.empresa != self.request.user.empresa:
                    raise PermissionDenied("No puede acceder a datos de otra empresa")
    
    def verificar_acceso_sucursal(self, sucursal):
        """Verificar acceso a sucursal"""
        if not self.request.user.puede_acceder_sucursal(sucursal):
            raise PermissionDenied("No tiene acceso a esta sucursal")

# ===========================================
# PERMISOS DE CONFIGURACIÓN
# ===========================================

class PuedeModificarConfiguracion(permissions.BasePermission):
    """Permiso para modificar configuración del sistema"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Solo administradores pueden modificar configuración
        return request.user.rol in ['administrador'] or request.user.is_superuser

class PuedeVerConfiguracion(permissions.BasePermission):
    """Permiso para ver configuración del sistema"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Administradores y contadores pueden ver configuración
        return request.user.rol in ['administrador', 'contador'] or request.user.is_superuser