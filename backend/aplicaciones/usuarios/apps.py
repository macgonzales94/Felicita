"""
CONFIGURACIÓN APP USUARIOS - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsuariosConfig(AppConfig):
    """
    Configuración de la aplicación Usuarios
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aplicaciones.usuarios'
    verbose_name = 'FELICITA - Gestión de Usuarios'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista
        """
        # Importar signals
        try:
            from . import signals
        except ImportError:
            pass
        
        # Conectar signal para crear roles iniciales
        post_migrate.connect(self.crear_roles_iniciales, sender=self)
    
    def crear_roles_iniciales(self, sender, **kwargs):
        """
        Crear roles iniciales del sistema
        """
        from .models import Rol, PermisoPersonalizado
        
        # Roles por defecto
        roles_default = [
            {
                'nombre': 'Administrador',
                'descripcion': 'Acceso completo al sistema',
                'es_rol_sistema': True,
                'permisos_especiales': {
                    'todos_los_modulos': True,
                    'gestionar_usuarios': True,
                    'configurar_sistema': True,
                    'ver_reportes_financieros': True,
                    'aprobar_documentos': True,
                    'eliminar_registros': True
                }
            },
            {
                'nombre': 'Contador',
                'descripcion': 'Acceso a módulos contables y facturación',
                'es_rol_sistema': True,
                'permisos_especiales': {
                    'facturacion': True,
                    'contabilidad': True,
                    'reportes': True,
                    'clientes': True,
                    'productos': True,
                    'aprobar_documentos': True
                }
            },
            {
                'nombre': 'Vendedor',
                'descripcion': 'Acceso a punto de venta e inventario básico',
                'es_rol_sistema': True,
                'permisos_especiales': {
                    'punto_venta': True,
                    'inventario_consulta': True,
                    'clientes': True,
                    'productos_consulta': True,
                    'crear_facturas': True
                }
            },
            {
                'nombre': 'Almacenero',
                'descripcion': 'Acceso completo a inventarios y almacenes',
                'es_rol_sistema': True,
                'permisos_especiales': {
                    'inventario': True,
                    'productos': True,
                    'transferencias': True,
                    'movimientos_inventario': True,
                    'reportes_inventario': True
                }
            },
            {
                'nombre': 'Consulta',
                'descripcion': 'Solo consulta de información',
                'es_rol_sistema': True,
                'permisos_especiales': {
                    'solo_consulta': True,
                    'reportes_basicos': True
                }
            }
        ]
        
        try:
            # Crear roles que no existen
            for rol_data in roles_default:
                Rol.objects.get_or_create(
                    nombre=rol_data['nombre'],
                    defaults=rol_data
                )
        except Exception as e:
            print(f"Warning: No se pudieron crear roles iniciales: {e}")
        
        # Permisos personalizados
        self.crear_permisos_personalizados()
    
    def crear_permisos_personalizados(self):
        """
        Crear permisos personalizados del sistema FELICITA
        """
        from .models import PermisoPersonalizado
        
        permisos_default = [
            # Facturación
            {'nombre': 'Crear Facturas', 'codigo': 'facturacion.crear', 'modulo': 'facturacion', 'accion': 'crear'},
            {'nombre': 'Anular Facturas', 'codigo': 'facturacion.anular', 'modulo': 'facturacion', 'accion': 'anular', 'es_critico': True},
            {'nombre': 'Aprobar Facturas', 'codigo': 'facturacion.aprobar', 'modulo': 'facturacion', 'accion': 'aprobar'},
            
            # Inventario
            {'nombre': 'Crear Productos', 'codigo': 'inventario.crear_producto', 'modulo': 'inventario', 'accion': 'crear'},
            {'nombre': 'Modificar Stock', 'codigo': 'inventario.modificar_stock', 'modulo': 'inventario', 'accion': 'actualizar'},
            {'nombre': 'Transferir Productos', 'codigo': 'inventario.transferir', 'modulo': 'inventario', 'accion': 'actualizar'},
            
            # Contabilidad
            {'nombre': 'Crear Asientos', 'codigo': 'contabilidad.crear_asientos', 'modulo': 'contabilidad', 'accion': 'crear'},
            {'nombre': 'Cerrar Períodos', 'codigo': 'contabilidad.cerrar_periodo', 'modulo': 'contabilidad', 'accion': 'actualizar', 'es_critico': True},
            
            # Reportes
            {'nombre': 'Ver Reportes Financieros', 'codigo': 'reportes.financieros', 'modulo': 'reportes', 'accion': 'leer'},
            {'nombre': 'Exportar Datos', 'codigo': 'reportes.exportar', 'modulo': 'reportes', 'accion': 'exportar'},
            
            # Configuración
            {'nombre': 'Configurar Sistema', 'codigo': 'configuracion.sistema', 'modulo': 'configuracion', 'accion': 'configurar', 'es_critico': True},
            {'nombre': 'Gestionar Usuarios', 'codigo': 'usuarios.gestionar', 'modulo': 'usuarios', 'accion': 'actualizar'},
        ]
        
        try:
            for permiso_data in permisos_default:
                PermisoPersonalizado.objects.get_or_create(
                    codigo=permiso_data['codigo'],
                    defaults=permiso_data
                )
        except Exception as e:
            print(f"Warning: No se pudieron crear permisos personalizados: {e}")
    
    def get_version(self):
        """
        Obtener versión de la aplicación
        """
        return "1.0.0"
    
    def get_description(self):
        """
        Obtener descripción de la aplicación
        """
        return "Módulo de gestión de usuarios, roles y permisos de FELICITA"