"""
PERMISSIONS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Clases de permisos personalizados para control de acceso por módulos
"""

from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class TienePermisoModulo(BasePermission):
    """
    Permiso personalizado para verificar permisos por módulo y acción
    """
    
    def has_permission(self, request, view):
        """
        Verificar si el usuario tiene permisos para el módulo
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Para superusuarios siempre permitir
        if request.user.is_superuser:
            return True
            
        # Determinar módulo y acción desde la vista
        modulo = self._obtener_modulo(view)
        accion = self._obtener_accion(request.method, view.action if hasattr(view, 'action') else None)
        
        # Verificar permisos específicos del usuario
        return self._usuario_tiene_permiso(request.user, modulo, accion)
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar permisos a nivel de objeto
        """
        if not self.has_permission(request, view):
            return False
            
        # Verificar que el objeto pertenece a la empresa del usuario
        if hasattr(obj, 'empresa') and hasattr(request.user, 'empresa'):
            return obj.empresa == request.user.empresa
            
        return True
    
    def _obtener_modulo(self, view):
        """
        Obtener el módulo desde el nombre de la vista
        """
        view_name = view.__class__.__name__.lower()
        
        if 'factura' in view_name or 'boleta' in view_name or 'nota' in view_name:
            return 'facturacion'
        elif 'inventario' in view_name or 'producto' in view_name:
            return 'inventario'
        elif 'contabilidad' in view_name or 'asiento' in view_name or 'balance' in view_name:
            return 'contabilidad'
        elif 'usuario' in view_name or 'rol' in view_name:
            return 'usuarios'
        elif 'cliente' in view_name or 'proveedor' in view_name:
            return 'clientes'
        elif 'reporte' in view_name:
            return 'reportes'
        elif 'guia' in view_name:
            return 'facturacion'
        else:
            return 'general'
    
    def _obtener_accion(self, method, action):
        """
        Obtener la acción desde el método HTTP y acción de la vista
        """
        if action:
            # Acciones específicas de ViewSet
            if action in ['create']:
                return 'crear'
            elif action in ['list', 'retrieve']:
                return 'leer'
            elif action in ['update', 'partial_update']:
                return 'actualizar'
            elif action in ['destroy']:
                return 'eliminar'
            elif action in ['enviar_sunat', 'anular']:
                return 'aprobar'
            elif action in ['descargar_xml', 'descargar_pdf']:
                return 'imprimir'
            else:
                return 'leer'
        else:
            # Métodos HTTP básicos
            if method == 'POST':
                return 'crear'
            elif method in ['GET', 'HEAD', 'OPTIONS']:
                return 'leer'
            elif method in ['PUT', 'PATCH']:
                return 'actualizar'
            elif method == 'DELETE':
                return 'eliminar'
            else:
                return 'leer'
    
    def _usuario_tiene_permiso(self, usuario, modulo, accion):
        """
        Verificar si el usuario tiene el permiso específico
        """
        # Si el usuario es admin de empresa, tiene todos los permisos de su empresa
        if hasattr(usuario, 'es_admin_empresa') and usuario.es_admin_empresa:
            return True
        
        # Verificar permisos a través de roles
        if hasattr(usuario, 'roles'):
            for usuario_rol in usuario.roles.filter(activo=True):
                if self._rol_tiene_permiso(usuario_rol.rol, modulo, accion):
                    return True
        
        # Verificar permisos directos del usuario (implementar según necesidad)
        # Por ahora, permitir a todos los usuarios autenticados
        return True
    
    def _rol_tiene_permiso(self, rol, modulo, accion):
        """
        Verificar si el rol tiene el permiso específico
        """
        if not rol.activo:
            return False
            
        # Verificar permisos especiales del rol
        permisos_especiales = rol.permisos_especiales or {}
        
        # Si tiene acceso completo al módulo
        if permisos_especiales.get(modulo) is True:
            return True
            
        # Verificar permisos específicos por acción
        permiso_key = f"{modulo}_{accion}"
        if permisos_especiales.get(permiso_key) is True:
            return True
            
        # Verificar si es solo consulta y tiene permiso de lectura
        if accion == 'leer' and permisos_especiales.get('solo_consulta') is True:
            return True
            
        return False


class TienePermisoEmpresa(BasePermission):
    """
    Permiso para verificar que el usuario pertenece a la empresa
    """
    
    def has_permission(self, request, view):
        """
        Verificar que el usuario está autenticado y tiene empresa
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        return hasattr(request.user, 'empresa') and request.user.empresa is not None
    
    def has_object_permission(self, request, view, obj):
        """
        Verificar que el objeto pertenece a la empresa del usuario
        """
        if not self.has_permission(request, view):
            return False
            
        if request.user.is_superuser:
            return True
            
        # Verificar que el objeto pertenece a la empresa del usuario
        if hasattr(obj, 'empresa') and hasattr(request.user, 'empresa'):
            return obj.empresa == request.user.empresa
            
        return False


class SoloLectura(BasePermission):
    """
    Permiso de solo lectura - permite solo métodos GET, HEAD, OPTIONS
    """
    
    def has_permission(self, request, view):
        """
        Solo permitir métodos de lectura
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user and request.user.is_authenticated
        return False


class EsAdminEmpresa(BasePermission):
    """
    Permiso para verificar que el usuario es administrador de empresa
    """
    
    def has_permission(self, request, view):
        """
        Verificar que el usuario es admin de empresa
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        return (
            hasattr(request.user, 'es_admin_empresa') and 
            request.user.es_admin_empresa
        )


class PuedeAprobar(BasePermission):
    """
    Permiso para usuarios que pueden aprobar facturas u otros documentos
    """
    
    def has_permission(self, request, view):
        """
        Verificar que el usuario puede aprobar
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        return (
            hasattr(request.user, 'puede_aprobar_facturas') and 
            request.user.puede_aprobar_facturas
        )


class TienePermisoInventario(BasePermission):
    """
    Permiso específico para módulo de inventario
    """
    
    def has_permission(self, request, view):
        """
        Verificar permisos específicos de inventario
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Verificar roles con permisos de inventario
        if hasattr(request.user, 'roles'):
            for usuario_rol in request.user.roles.filter(activo=True):
                permisos = usuario_rol.rol.permisos_especiales or {}
                if permisos.get('inventario') or permisos.get('productos'):
                    return True
        
        return False


class TienePermisoContabilidad(BasePermission):
    """
    Permiso específico para módulo de contabilidad
    """
    
    def has_permission(self, request, view):
        """
        Verificar permisos específicos de contabilidad
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Verificar roles con permisos de contabilidad
        if hasattr(request.user, 'roles'):
            for usuario_rol in request.user.roles.filter(activo=True):
                permisos = usuario_rol.rol.permisos_especiales or {}
                if permisos.get('contabilidad') or permisos.get('asientos'):
                    return True
        
        return False


class TienePermisoReportes(BasePermission):
    """
    Permiso específico para módulo de reportes
    """
    
    def has_permission(self, request, view):
        """
        Verificar permisos específicos de reportes
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # Verificar roles con permisos de reportes
        if hasattr(request.user, 'roles'):
            for usuario_rol in request.user.roles.filter(activo=True):
                permisos = usuario_rol.rol.permisos_especiales or {}
                if (permisos.get('reportes') or 
                    permisos.get('reportes_basicos') or 
                    permisos.get('reportes_financieros')):
                    return True
        
        return False