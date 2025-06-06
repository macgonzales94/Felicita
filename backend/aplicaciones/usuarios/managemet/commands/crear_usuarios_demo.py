"""
Comando para crear usuarios de demostración para FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.hashers import make_password
from aplicaciones.usuarios.models import Usuario, RolUsuario, LogActividad
from aplicaciones.empresas.models import Empresa


class Command(BaseCommand):
    help = 'Crear usuarios de demostración para desarrollo local de FELICITA'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa-id',
            type=int,
            default=1,
            help='ID de la empresa para asignar a los usuarios (default: 1)'
        )
        
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Eliminar usuarios existentes antes de crear nuevos'
        )
        
        parser.add_argument(
            '--password',
            type=str,
            default='felicita123',
            help='Contraseña para todos los usuarios demo (default: felicita123)'
        )
    
    def handle(self, *args, **options):
        empresa_id = options['empresa_id']
        reset = options['reset']
        password = options['password']
        
        try:
            with transaction.atomic():
                # Verificar que la empresa existe
                try:
                    empresa = Empresa.objects.get(id=empresa_id)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Empresa encontrada: {empresa.razon_social}')
                    )
                except Empresa.DoesNotExist:
                    raise CommandError(f'❌ Empresa con ID {empresa_id} no existe')
                
                # Eliminar usuarios existentes si se especifica reset
                if reset:
                    usuarios_existentes = Usuario.objects.filter(
                        username__in=['admin', 'contador', 'vendedor1', 'vendedor2', 'cliente_demo']
                    )
                    count = usuarios_existentes.count()
                    usuarios_existentes.delete()
                    self.stdout.write(
                        self.style.WARNING(f'🗑️ Eliminados {count} usuarios existentes')
                    )
                
                # Crear usuarios de demostración
                usuarios_demo = [
                    {
                        'username': 'admin',
                        'email': 'admin@felicita.pe',
                        'first_name': 'Administrador',
                        'last_name': 'FELICITA',
                        'rol': RolUsuario.ADMINISTRADOR,
                        'numero_documento': '12345678',
                        'tipo_documento': '1',
                        'telefono': '+51 987654321',
                        'direccion': 'Lima, Perú',
                        'is_staff': True,
                        'is_superuser': True,
                        'permisos_especiales': {},
                        'configuraciones': {
                            'tema_preferido': 'claro',
                            'idioma': 'es-pe',
                            'notificaciones_email': True,
                            'dashboard_widgets': ['ventas', 'inventario', 'clientes', 'contabilidad']
                        }
                    },
                    {
                        'username': 'contador',
                        'email': 'contador@felicita.pe',
                        'first_name': 'María Elena',
                        'last_name': 'Rodríguez Vega',
                        'rol': RolUsuario.CONTADOR,
                        'numero_documento': '87654321',
                        'tipo_documento': '1',
                        'telefono': '+51 987123456',
                        'direccion': 'San Isidro, Lima',
                        'is_staff': False,
                        'is_superuser': False,
                        'permisos_especiales': {
                            'facturacion': {
                                'ver': True,
                                'crear': True,
                                'editar': True,
                                'eliminar': False,
                                'anular': True
                            },
                            'contabilidad': {
                                'ver': True,
                                'crear': True,
                                'editar': True,
                                'eliminar': False,
                                'confirmar_asientos': True
                            },
                            'reportes': {
                                'ver': True,
                                'exportar': True,
                                'ple': True
                            }
                        },
                        'configuraciones': {
                            'tema_preferido': 'claro',
                            'idioma': 'es-pe',
                            'notificaciones_email': True,
                            'dashboard_widgets': ['contabilidad', 'reportes', 'facturacion']
                        }
                    },
                    {
                        'username': 'vendedor1',
                        'email': 'vendedor1@felicita.pe',
                        'first_name': 'Carlos Alberto',
                        'last_name': 'Mendoza Silva',
                        'rol': RolUsuario.VENDEDOR,
                        'numero_documento': '45678912',
                        'tipo_documento': '1',
                        'telefono': '+51 987789123',
                        'direccion': 'Miraflores, Lima',
                        'is_staff': False,
                        'is_superuser': False,
                        'permisos_especiales': {
                            'pos': {
                                'ver': True,
                                'crear': True,
                                'procesar_ventas': True
                            },
                            'facturacion': {
                                'ver': True,
                                'crear': True,
                                'editar': False,
                                'eliminar': False
                            },
                            'clientes': {
                                'ver': True,
                                'crear': True,
                                'editar': True
                            },
                            'productos': {
                                'ver': True,
                                'editar_precios': False
                            }
                        },
                        'configuraciones': {
                            'tema_preferido': 'claro',
                            'idioma': 'es-pe',
                            'notificaciones_email': False,
                            'dashboard_widgets': ['pos', 'ventas', 'clientes']
                        }
                    },
                    {
                        'username': 'vendedor2',
                        'email': 'vendedor2@felicita.pe',
                        'first_name': 'Ana Lucía',
                        'last_name': 'Torres Ramírez',
                        'rol': RolUsuario.VENDEDOR,
                        'numero_documento': '78912345',
                        'tipo_documento': '1',
                        'telefono': '+51 987456789',
                        'direccion': 'San Borja, Lima',
                        'is_staff': False,
                        'is_superuser': False,
                        'permisos_especiales': {
                            'pos': {
                                'ver': True,
                                'crear': True,
                                'procesar_ventas': True
                            },
                            'facturacion': {
                                'ver': True,
                                'crear': True,
                                'editar': False,
                                'eliminar': False
                            },
                            'clientes': {
                                'ver': True,
                                'crear': True,
                                'editar': True
                            },
                            'productos': {
                                'ver': True,
                                'editar_precios': False
                            }
                        },
                        'configuraciones': {
                            'tema_preferido': 'oscuro',
                            'idioma': 'es-pe',
                            'notificaciones_email': True,
                            'dashboard_widgets': ['pos', 'ventas', 'inventario']
                        }
                    },
                    {
                        'username': 'cliente_demo',
                        'email': 'cliente@demo.com',
                        'first_name': 'Cliente',
                        'last_name': 'Demo',
                        'rol': RolUsuario.CLIENTE,
                        'numero_documento': '98765432',
                        'tipo_documento': '1',
                        'telefono': '+51 987111222',
                        'direccion': 'Lima, Perú',
                        'is_staff': False,
                        'is_superuser': False,
                        'permisos_especiales': {
                            'consultas': {
                                'ver': True,
                                'propios_comprobantes': True
                            }
                        },
                        'configuraciones': {
                            'tema_preferido': 'claro',
                            'idioma': 'es-pe',
                            'notificaciones_email': False,
                            'dashboard_widgets': ['consultas']
                        }
                    }
                ]
                
                usuarios_creados = []
                
                for user_data in usuarios_demo:
                    # Verificar si el usuario ya existe
                    if Usuario.objects.filter(username=user_data['username']).exists():
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Usuario {user_data["username"]} ya existe, omitiendo...')
                        )
                        continue
                    
                    # Crear usuario
                    usuario = Usuario.objects.create(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        password=make_password(password),
                        numero_documento=user_data['numero_documento'],
                        tipo_documento=user_data['tipo_documento'],
                        telefono=user_data['telefono'],
                        direccion=user_data['direccion'],
                        rol=user_data['rol'],
                        empresa=empresa,
                        is_active=True,
                        is_staff=user_data.get('is_staff', False),
                        is_superuser=user_data.get('is_superuser', False),
                        permisos_especiales=user_data.get('permisos_especiales', {}),
                        configuraciones=user_data.get('configuraciones', {}),
                        tema_preferido=user_data['configuraciones'].get('tema_preferido', 'claro'),
                        idioma=user_data['configuraciones'].get('idioma', 'es-pe')
                    )
                    
                    usuarios_creados.append(usuario)
                    
                    # Registrar en log de actividad
                    LogActividad.registrar_actividad(
                        usuario=usuario,
                        accion='CREAR_USUARIO_DEMO',
                        modulo='ADMINISTRACION',
                        descripcion=f'Usuario demo creado: {usuario.username}',
                        datos_adicionales={
                            'comando': 'crear_usuarios_demo',
                            'rol': usuario.rol
                        },
                        direccion_ip='127.0.0.1'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Usuario creado: {usuario.username} ({usuario.get_rol_display()}) - {usuario.email}'
                        )
                    )
                
                # Mostrar resumen
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS('🎉 USUARIOS DEMO CREADOS EXITOSAMENTE'))
                self.stdout.write('='*50)
                
                self.stdout.write(f'📊 Total usuarios creados: {len(usuarios_creados)}')
                self.stdout.write(f'🏢 Empresa asignada: {empresa.razon_social}')
                self.stdout.write(f'🔑 Contraseña para todos: {password}')
                
                self.stdout.write('\n📋 CREDENCIALES DE ACCESO:')
                for usuario in usuarios_creados:
                    self.stdout.write(
                        f'   • {usuario.username} / {password} ({usuario.get_rol_display()})'
                    )
                
                self.stdout.write('\n🌐 URLs DE DESARROLLO:')
                self.stdout.write('   • Backend API: http://localhost:8000')
                self.stdout.write('   • Admin Django: http://localhost:8000/admin')
                self.stdout.write('   • API Docs: http://localhost:8000/api/docs/')
                self.stdout.write('   • Frontend: http://localhost:3000 (cuando esté disponible)')
                
                self.stdout.write('\n💡 TIPS DE USO:')
                self.stdout.write('   • admin: Acceso completo al sistema')
                self.stdout.write('   • contador: Facturación, contabilidad y reportes')
                self.stdout.write('   • vendedor1/vendedor2: Punto de venta y clientes')
                self.stdout.write('   • cliente_demo: Solo consulta de comprobantes')
                
                self.stdout.write('\n🔧 COMANDOS ÚTILES:')
                self.stdout.write('   python manage.py crear_usuarios_demo --reset  # Recrear usuarios')
                self.stdout.write('   python manage.py crear_usuarios_demo --password nueva123  # Cambiar contraseña')
                
        except Exception as e:
            raise CommandError(f'❌ Error creando usuarios demo: {str(e)}')
    
    def crear_configuraciones_por_defecto(self, usuario):
        """
        Crear configuraciones por defecto para un usuario
        """
        configuraciones_base = {
            'dashboard_configuracion': {
                'widgets_activos': ['ventas_hoy', 'stock_bajo', 'cuentas_por_cobrar'],
                'layout': 'grid',
                'actualizacion_automatica': True
            },
            'notificaciones': {
                'email_nuevos_comprobantes': True,
                'email_stock_bajo': True,
                'email_cuentas_vencidas': False,
                'push_browser': True
            },
            'preferencias_ui': {
                'mostrar_ayudas': True,
                'animaciones': True,
                'sonidos': False,
                'compacto': False
            },
            'accesos_rapidos': [
                {'nombre': 'Nueva Factura', 'ruta': '/facturacion/nueva'},
                {'nombre': 'Consultar Stock', 'ruta': '/inventarios/stock'},
                {'nombre': 'Reportes', 'ruta': '/reportes/dashboard'}
            ]
        }
        
        # Personalizar según rol
        if usuario.rol == RolUsuario.VENDEDOR:
            configuraciones_base['accesos_rapidos'] = [
                {'nombre': 'Punto de Venta', 'ruta': '/pos'},
                {'nombre': 'Nueva Venta', 'ruta': '/pos/nueva'},
                {'nombre': 'Clientes', 'ruta': '/clientes'}
            ]
        elif usuario.rol == RolUsuario.CONTADOR:
            configuraciones_base['accesos_rapidos'] = [
                {'nombre': 'Asientos Contables', 'ruta': '/contabilidad/asientos'},
                {'nombre': 'Balance General', 'ruta': '/reportes/balance'},
                {'nombre': 'Estado Resultados', 'ruta': '/reportes/resultados'}
            ]
        
        usuario.configuraciones.update(configuraciones_base)
        usuario.save(update_fields=['configuraciones'])