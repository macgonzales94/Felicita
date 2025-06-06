"""
Permisos personalizados para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import RolUsuario


class EsAdministrador(BasePermission):
    """
    Permiso que solo permite acceso a administradores del sistema
    """
    message = 'Solo los administradores pueden realizar esta acción.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.es_administrador()


class EsContador(BasePermission):
    """
    Permiso que solo permite acceso a contadores y administradores
    """
    message = 'Solo los contadores y administradores pueden realizar esta acción.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.es_contador() or request.user.es_administrador()


class EsVendedor(BasePermission):
    """
    Permiso que permite acceso a vendedores, contadores y administradores
    """
    message = 'Solo el personal autorizado puede realizar esta acción.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.es_vendedor() or request.user.es_contador() or request.user.es_administrador()


class PermisosModuloFacturacion(BasePermission):
    """
    Permisos específicos para el módulo de facturación
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores tienen acceso completo
        if request.user.es_administrador():
            return True
        
        # Determinar acción según método HTTP
        acciones_por_metodo = {
            'GET': 'ver',
            'POST': 'crear',
            'PUT': 'editar',
            'PATCH': 'editar',
            'DELETE': 'eliminar'
        }
        
        accion = acciones_por_metodo.get(request.method, 'ver')
        
        # Verificar permiso específico
        return request.user.tiene_permiso('facturacion', accion)
    
    def has_object_permission(self, request, view, obj):
        """Verificar permisos a nivel de objeto"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores pueden todo
        if request.user.es_administrador():
            return True
        
        # Verificar que el objeto pertenece a la misma empresa
        if hasattr(obj, 'empresa') and obj.empresa != request.user.empresa:
            return False
        
        # Para vendedores, solo pueden ver/editar sus propios comprobantes
        if request.user.es_vendedor():
            if hasattr(obj, 'usuario_creacion'):
                return obj.usuario_creacion == request.user
        
        return True


class PermisosModuloInventario(BasePermission):
    """
    Permisos específicos para el módulo de inventario
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.es_administrador():
            return True
        
        acciones_por_metodo = {
            'GET': 'ver',
            'POST': 'crear',
            'PUT': 'editar',
            'PATCH': 'editar',
            'DELETE': 'eliminar'
        }
        
        accion = acciones_por_metodo.get(request.method, 'ver')
        return request.user.tiene_permiso('inventarios', accion)


class PermisosModuloContabilidad(BasePermission):
    """
    Permisos específicos para el módulo de contabilidad
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Solo contadores y administradores pueden acceder a contabilidad
        if not (request.user.es_contador() or request.user.es_administrador()):
            return False
        
        acciones_por_metodo = {
            'GET': 'ver',
            'POST': 'crear',
            'PUT': 'editar',
            'PATCH': 'editar',
            'DELETE': 'eliminar'
        }
        
        accion = acciones_por_metodo.get(request.method, 'ver')
        return request.user.tiene_permiso('contabilidad', accion)


class PermisosModuloReportes(BasePermission):
    """
    Permisos específicos para el módulo de reportes
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.es_administrador():
            return True
        
        # Los reportes generalmente solo requieren permiso de lectura
        return request.user.tiene_permiso('reportes', 'ver')


class PermisosModuloPOS(BasePermission):
    """
    Permisos específicos para el módulo de punto de venta
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.es_administrador():
            return True
        
        # Solo vendedores y contadores pueden usar POS
        if not (request.user.es_vendedor() or request.user.es_contador()):
            return False
        
        acciones_por_metodo = {
            'GET': 'ver',
            'POST': 'crear',
            'PUT': 'editar',
            'PATCH': 'editar',
            'DELETE': 'eliminar'
        }
        
        accion = acciones_por_metodo.get(request.method, 'ver')
        return request.user.tiene_permiso('pos', accion)


class PermisosModuloConfiguraciones(BasePermission):
    """
    Permisos específicos para el módulo de configuraciones
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Solo administradores pueden modificar configuraciones del sistema
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.es_administrador()
        
        # Todos los usuarios autenticados pueden ver configuraciones básicas
        return True


class SoloLeerOPropioUsuario(BasePermission):
    """
    Permite solo lectura o modificación del propio perfil de usuario
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores pueden gestionar cualquier usuario
        if request.user.es_administrador():
            return True
        
        # Los usuarios solo pueden ver/editar su propio perfil
        return obj == request.user


class PermisosEmpresa(BasePermission):
    """
    Verifica que el usuario pertenece a la misma empresa que el objeto
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Usuarios deben tener empresa asignada
        return hasattr(request.user, 'empresa') and request.user.empresa is not None
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusuarios pueden acceder a todo
        if request.user.is_superuser:
            return True
        
        # Verificar que el objeto pertenece a la misma empresa
        if hasattr(obj, 'empresa'):
            return obj.empresa == request.user.empresa
        
        # Si el objeto no tiene empresa, permitir acceso
        return True


class PermisosAlmacen(BasePermission):
    """
    Permisos específicos para almacenes según configuración del usuario
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores pueden acceder a todos los almacenes
        if request.user.es_administrador():
            return True
        
        # Verificar almacenes permitidos para el usuario
        almacenes_permitidos = request.user.obtener_almacenes_permitidos()
        
        # Si el objeto es un almacén
        if hasattr(obj, 'almacen'):
            return obj.almacen in almacenes_permitidos
        elif obj.__class__.__name__ == 'Almacen':
            return obj in almacenes_permitidos
        
        return True


class PermisosPrecios(BasePermission):
    """
    Permisos específicos para modificación de precios
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Solo verificar en métodos que modifican
        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.puede_modificar_precios()
        
        return True


class PermisosDescuentos(BasePermission):
    """
    Permisos específicos para aprobación de descuentos
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Solo verificar en acciones que requieren aprobación de descuentos
        if hasattr(view, 'action') and view.action in ['aprobar_descuento', 'aplicar_descuento']:
            return request.user.puede_aprobar_descuentos()
        
        return True


class PermisosCombinadosFacturacion(permissions.DjangoModelPermissions):
    """
    Permisos combinados para facturación usando Django perms + permisos personalizados
    """
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
    
    def has_permission(self, request, view):
        # Verificar permisos Django base
        django_perms = super().has_permission(request, view)
        
        # Verificar permisos personalizados de FELICITA
        felicita_perms = PermisosModuloFacturacion().has_permission(request, view)
        
        # Verificar permisos de empresa
        empresa_perms = PermisosEmpresa().has_permission(request, view)
        
        return django_perms and felicita_perms and empresa_perms


# Funciones de utilidad para verificar permisos

def verificar_permiso_modulo(usuario, modulo, accion='ver'):
    """
    Función utilitaria para verificar permisos de módulo
    """
    if not usuario or not usuario.is_authenticated:
        return False
    
    if usuario.es_administrador():
        return True
    
    return usuario.tiene_permiso(modulo, accion)


def verificar_acceso_empresa(usuario, objeto):
    """
    Función utilitaria para verificar acceso por empresa
    """
    if not usuario or not usuario.is_authenticated:
        return False
    
    if usuario.is_superuser:
        return True
    
    if hasattr(objeto, 'empresa'):
        return objeto.empresa == usuario.empresa
    
    return True


def obtener_queryset_por_empresa(usuario, queryset):
    """
    Función utilitaria para filtrar queryset por empresa del usuario
    """
    if not usuario or not usuario.is_authenticated:
        return queryset.none()
    
    if usuario.is_superuser:
        return queryset
    
    if hasattr(usuario, 'empresa') and usuario.empresa:
        return queryset.filter(empresa=usuario.empresa)
    
    return queryset.none()


def obtener_queryset_por_almacenes_permitidos(usuario, queryset):
    """
    Función utilitaria para filtrar por almacenes permitidos
    """
    if not usuario or not usuario.is_authenticated:
        return queryset.none()
    
    if usuario.es_administrador():
        return queryset
    
    almacenes_permitidos = usuario.obtener_almacenes_permitidos()
    
    if hasattr(queryset.model, 'almacen'):
        return queryset.filter(almacen__in=almacenes_permitidos)
    
    return queryset


# Decorador para verificar permisos en vistas basadas en funciones

def requiere_permiso(modulo, accion='ver'):
    """
    Decorador para verificar permisos en vistas basadas en funciones
    """
    def decorador(vista):
        def vista_decorada(request, *args, **kwargs):
            if not verificar_permiso_modulo(request.user, modulo, accion):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(f'No tiene permisos para {accion} en el módulo {modulo}')
            
            return vista(request, *args, **kwargs)
        
        return vista_decorada
    return decorador