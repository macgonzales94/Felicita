"""
FELICITA - Comando de Inicialización
Sistema de Facturación Electrónica para Perú

Comando para inicializar datos de prueba y configuración inicial
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from django.core.management import call_command
from aplicaciones.core.models import (
    Empresa, Sucursal, TipoComprobante, SerieComprobante, 
    Cliente, Configuracion
)
from aplicaciones.usuarios.models import Usuario
import sys
import json

class Command(BaseCommand):
    help = 'Inicializa FELICITA con datos de prueba y configuración base'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Omitir ejecución de migraciones',
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Omitir creación de usuarios de prueba',
        )
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Omitir creación de datos base',
        )
        parser.add_argument(
            '--production',
            action='store_true',
            help='Modo producción (solo datos esenciales)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar inicialización incluso si ya existen datos',
        )

    def handle(self, *args, **options):
        """Ejecutar inicialización completa"""
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando configuración de FELICITA...')
        )
        
        try:
            # Verificar si ya existe configuración
            if not options['force'] and self._has_existing_data():
                self.stdout.write(
                    self.style.WARNING('⚠️  Ya existen datos en el sistema.')
                )
                response = input('¿Desea continuar? (s/N): ')
                if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
                    self.stdout.write(
                        self.style.ERROR('❌ Inicialización cancelada.')
                    )
                    return
            
            # Ejecutar migraciones
            if not options['skip_migrations']:
                self._run_migrations()
            
            # Crear datos base
            if not options['skip_data']:
                self._create_base_data(options['production'])
            
            # Crear usuarios de prueba
            if not options['skip_users'] and not options['production']:
                self._create_test_users()
            
            # Configuración final
            self._final_setup()
            
            self.stdout.write(
                self.style.SUCCESS('✅ FELICITA inicializado correctamente!')
            )
            self._show_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la inicialización: {e}')
            )
            raise CommandError(f'Fallo en la inicialización: {e}')

    def _has_existing_data(self):
        """Verificar si ya existen datos en el sistema"""
        return (
            Usuario.objects.filter(is_superuser=True).exists() or
            Empresa.objects.exists() or
            TipoComprobante.objects.exists()
        )

    def _run_migrations(self):
        """Ejecutar migraciones de Django"""
        self.stdout.write('📦 Ejecutando migraciones...')
        
        try:
            call_command('migrate', verbosity=0, interactive=False)
            self.stdout.write(
                self.style.SUCCESS('✅ Migraciones ejecutadas correctamente')
            )
        except Exception as e:
            raise CommandError(f'Error en migraciones: {e}')

    @transaction.atomic
    def _create_base_data(self, production_mode=False):
        """Crear datos base del sistema"""
        self.stdout.write('🏢 Creando datos base...')
        
        # Crear tipos de comprobante SUNAT
        self._create_tipos_comprobante()
        
        # Crear empresa demo
        empresa = self._create_empresa_demo(production_mode)
        
        # Crear sucursal principal
        sucursal = self._create_sucursal_principal(empresa)
        
        # Crear series de comprobantes
        self._create_series_comprobante(empresa, sucursal)
        
        # Crear configuración base
        self._create_configuracion_base(empresa)
        
        # Crear clientes de prueba (solo en desarrollo)
        if not production_mode:
            self._create_clientes_prueba(empresa)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Datos base creados correctamente')
        )

    def _create_tipos_comprobante(self):
        """Crear tipos de comprobante según SUNAT"""
        tipos_comprobante = [
            {
                'codigo': '01',
                'nombre': 'Factura',
                'descripcion': 'Factura Electrónica',
                'requiere_serie': True,
                'formato_serie': 'F###'
            },
            {
                'codigo': '03',
                'nombre': 'Boleta de Venta',
                'descripcion': 'Boleta de Venta Electrónica',
                'requiere_serie': True,
                'formato_serie': 'B###'
            },
            {
                'codigo': '07',
                'nombre': 'Nota de Crédito',
                'descripcion': 'Nota de Crédito Electrónica',
                'requiere_serie': True,
                'formato_serie': 'FC##'
            },
            {
                'codigo': '08',
                'nombre': 'Nota de Débito',
                'descripcion': 'Nota de Débito Electrónica',
                'requiere_serie': True,
                'formato_serie': 'FD##'
            },
            {
                'codigo': '09',
                'nombre': 'Guía de Remisión',
                'descripcion': 'Guía de Remisión Electrónica',
                'requiere_serie': True,
                'formato_serie': 'T###'
            }
        ]
        
        for tipo_data in tipos_comprobante:
            tipo, created = TipoComprobante.objects.get_or_create(
                codigo=tipo_data['codigo'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'  ➕ Tipo comprobante creado: {tipo.nombre}')

    def _create_empresa_demo(self, production_mode):
        """Crear empresa demo"""
        empresa_data = {
            'ruc': getattr(settings, 'EMPRESA_CONFIG', {}).get('ruc', '20123456789'),
            'razon_social': getattr(settings, 'EMPRESA_CONFIG', {}).get(
                'razon_social', 
                'EMPRESA DEMO SAC' if not production_mode else 'MI EMPRESA SAC'
            ),
            'nombre_comercial': 'FELICITA' if not production_mode else 'MI EMPRESA',
            'direccion_fiscal': getattr(settings, 'EMPRESA_CONFIG', {}).get(
                'direccion', 
                'AV. DEMO 123, LIMA, PERU'
            ),
            'ubigeo': '150101',  # Lima - Lima - Lima
            'telefono': getattr(settings, 'EMPRESA_CONFIG', {}).get('telefono', '01-1234567'),
            'email': getattr(settings, 'EMPRESA_CONFIG', {}).get('email', 'contacto@empresa.com'),
            'representante_legal': 'REPRESENTANTE LEGAL',
            'usuario_sol': 'USUARIO123456',
            'activo': True
        }
        
        empresa, created = Empresa.objects.get_or_create(
            ruc=empresa_data['ruc'],
            defaults=empresa_data
        )
        
        if created:
            self.stdout.write(f'  ➕ Empresa creada: {empresa.razon_social}')
        else:
            self.stdout.write(f'  ✓ Empresa existente: {empresa.razon_social}')
        
        return empresa

    def _create_sucursal_principal(self, empresa):
        """Crear sucursal principal"""
        sucursal_data = {
            'empresa': empresa,
            'codigo': '001',
            'nombre': 'Sucursal Principal',
            'direccion': empresa.direccion_fiscal,
            'ubigeo': empresa.ubigeo,
            'telefono': empresa.telefono,
            'email': empresa.email,
            'es_principal': True,
            'activo': True
        }
        
        sucursal, created = Sucursal.objects.get_or_create(
            empresa=empresa,
            codigo='001',
            defaults=sucursal_data
        )
        
        if created:
            self.stdout.write(f'  ➕ Sucursal creada: {sucursal.nombre}')
        
        return sucursal

    def _create_series_comprobante(self, empresa, sucursal):
        """Crear series de comprobante"""
        series_data = [
            {'tipo_codigo': '01', 'serie': 'F001'},
            {'tipo_codigo': '03', 'serie': 'B001'},
            {'tipo_codigo': '07', 'serie': 'FC01'},
            {'tipo_codigo': '08', 'serie': 'FD01'},
            {'tipo_codigo': '09', 'serie': 'T001'},
        ]
        
        for serie_data in series_data:
            try:
                tipo_comprobante = TipoComprobante.objects.get(
                    codigo=serie_data['tipo_codigo']
                )
                
                serie, created = SerieComprobante.objects.get_or_create(
                    empresa=empresa,
                    tipo_comprobante=tipo_comprobante,
                    serie=serie_data['serie'],
                    defaults={
                        'numero_actual': 0,
                        'sucursal': sucursal,
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  ➕ Serie creada: {serie.serie}')
                    
            except TipoComprobante.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Tipo de comprobante no encontrado: {serie_data["tipo_codigo"]}')
                )

    def _create_configuracion_base(self, empresa):
        """Crear configuración base del sistema"""
        config_data = {
            'empresa': empresa,
            'igv_porcentaje': 18.00,
            'moneda_defecto': 'PEN',
            'numeracion_automatica': True,
            'envio_automatico_sunat': False,  # Desactivado por defecto
            'envio_email_cliente': False,
            'metodo_valuacion': 'PEPS',
            'control_stock': True,
            'formato_fecha': 'DD/MM/YYYY',
            'activo': True
        }
        
        config, created = Configuracion.objects.get_or_create(
            empresa=empresa,
            defaults=config_data
        )
        
        if created:
            self.stdout.write('  ➕ Configuración base creada')

    def _create_clientes_prueba(self, empresa):
        """Crear clientes de prueba"""
        clientes_data = [
            {
                'empresa': empresa,
                'tipo_documento': 'dni',
                'numero_documento': '12345678',
                'razon_social': 'JUAN CARLOS PEREZ LOPEZ',
                'direccion': 'AV. EXAMPLE 123, LIMA',
                'ubigeo': '150101',
                'telefono': '999111222',
                'email': 'juan.perez@email.com',
                'contacto_principal': 'Juan Perez',
                'activo': True
            },
            {
                'empresa': empresa,
                'tipo_documento': 'ruc',
                'numero_documento': '20987654321',
                'razon_social': 'EMPRESA CLIENTE SAC',
                'nombre_comercial': 'CLIENTE SAC',
                'direccion': 'AV. CLIENTE 456, LIMA',
                'ubigeo': '150101',
                'telefono': '01-2345678',
                'email': 'contacto@clientesac.pe',
                'contacto_principal': 'Ana Gutierrez',
                'limite_credito': 10000.00,
                'dias_credito': 30,
                'activo': True
            }
        ]
        
        for cliente_data in clientes_data:
            cliente, created = Cliente.objects.get_or_create(
                empresa=empresa,
                numero_documento=cliente_data['numero_documento'],
                defaults=cliente_data
            )
            
            if created:
                self.stdout.write(f'  ➕ Cliente creado: {cliente.razon_social}')

    @transaction.atomic
    def _create_test_users(self):
        """Crear usuarios de prueba"""
        self.stdout.write('👥 Creando usuarios de prueba...')
        
        # Obtener empresa
        try:
            empresa = Empresa.objects.first()
        except Empresa.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('⚠️  No se encontró empresa para asignar usuarios')
            )
            return
        
        usuarios_data = [
            {
                'username': 'admin',
                'email': 'admin@felicita.pe',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'rol': 'administrador',
                'telefono': '999123456',
                'documento_identidad': '12345678',
                'is_superuser': True,
                'is_staff': True,
                'password': 'admin123'
            },
            {
                'username': 'contador',
                'email': 'contador@felicita.pe',
                'first_name': 'Maria',
                'last_name': 'Gonzales',
                'rol': 'contador',
                'telefono': '999123457',
                'documento_identidad': '12345679',
                'password': 'contador123'
            },
            {
                'username': 'vendedor',
                'email': 'vendedor@felicita.pe',
                'first_name': 'Carlos',
                'last_name': 'Rodriguez',
                'rol': 'vendedor',
                'telefono': '999123458',
                'documento_identidad': '12345680',
                'password': 'vendedor123'
            }
        ]
        
        for user_data in usuarios_data:
            password = user_data.pop('password')
            
            usuario, created = Usuario.objects.get_or_create(
                username=user_data['username'],
                defaults={**user_data, 'empresa': empresa}
            )
            
            if created:
                usuario.set_password(password)
                usuario.save()
                self.stdout.write(
                    f'  ➕ Usuario creado: {usuario.username} ({usuario.rol})'
                )
            else:
                self.stdout.write(
                    f'  ✓ Usuario existente: {usuario.username}'
                )

    def _final_setup(self):
        """Configuración final del sistema"""
        self.stdout.write('⚙️  Configuración final...')
        
        # Recopilar archivos estáticos en producción
        if not settings.DEBUG:
            call_command('collectstatic', verbosity=0, interactive=False)
            self.stdout.write('  ✅ Archivos estáticos recopilados')
        
        # Limpiar cache
        try:
            from django.core.cache import cache
            cache.clear()
            self.stdout.write('  ✅ Cache limpiado')
        except Exception:
            pass

    def _show_summary(self):
        """Mostrar resumen de la inicialización"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE INICIALIZACIÓN'))
        self.stdout.write('='*50)
        
        # Contar datos creados
        empresas_count = Empresa.objects.count()
        sucursales_count = Sucursal.objects.count()
        tipos_count = TipoComprobante.objects.count()
        series_count = SerieComprobante.objects.count()
        usuarios_count = Usuario.objects.count()
        clientes_count = Cliente.objects.count()
        
        self.stdout.write(f'🏢 Empresas: {empresas_count}')
        self.stdout.write(f'🏪 Sucursales: {sucursales_count}')
        self.stdout.write(f'📄 Tipos de comprobante: {tipos_count}')
        self.stdout.write(f'🔢 Series de comprobante: {series_count}')
        self.stdout.write(f'👥 Usuarios: {usuarios_count}')
        self.stdout.write(f'👤 Clientes: {clientes_count}')
        
        self.stdout.write('\n📋 USUARIOS DE ACCESO:')
        self.stdout.write('-' * 30)
        for usuario in Usuario.objects.all():
            self.stdout.write(
                f'  👤 {usuario.username} ({usuario.get_rol_display()}) - {usuario.email}'
            )
        
        self.stdout.write('\n🌐 ACCESOS AL SISTEMA:')
        self.stdout.write('-' * 30)
        self.stdout.write('  💻 Admin Django: http://localhost:8000/admin/')
        self.stdout.write('  📱 Frontend: http://localhost:3000/')
        self.stdout.write('  📖 API Docs: http://localhost:8000/api/docs/')
        self.stdout.write('  🔍 Health Check: http://localhost:8000/health/')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('🎉 ¡FELICITA está listo para usar!')
        )
        self.stdout.write('='*50)