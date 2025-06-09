#!/usr/bin/env python
"""
SCRIPT DE UTILIDADES - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Script para tareas de mantenimiento y administración del sistema
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
from decimal import Decimal
import subprocess

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felicita.configuracion.local')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.cache import cache
from django.conf import settings

# Importar modelos
from aplicaciones.core.models import (
    Empresa, Cliente, Producto, ConfiguracionSistema
)
from aplicaciones.usuarios.models import Usuario
from aplicaciones.facturacion.models import SerieComprobante

# Colores para consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'  # End color
    BOLD = '\033[1m'

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def print_header(title):
    """Imprimir encabezado"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
    print(f"🚀 FELICITA - {title}")
    print(f"{'='*60}{Colors.ENDC}\n")

def cargar_datos_iniciales():
    """Cargar datos iniciales del sistema"""
    print_header("CARGANDO DATOS INICIALES")
    
    try:
        # Verificar si ya existen datos
        if Empresa.objects.exists():
            print_warning("Ya existen empresas en el sistema. ¿Desea continuar? (s/n)")
            respuesta = input().lower()
            if respuesta != 's':
                print_info("Operación cancelada")
                return
        
        # Cargar fixtures
        call_command('loaddata', 'fixtures/datos_iniciales.json', verbosity=2)
        print_success("Datos iniciales cargados correctamente")
        
        # Crear series de comprobantes
        crear_series_comprobantes()
        
        # Mostrar resumen
        mostrar_resumen_datos()
        
    except Exception as e:
        print_error(f"Error al cargar datos iniciales: {e}")

def crear_series_comprobantes():
    """Crear series de comprobantes por defecto"""
    print_info("Creando series de comprobantes...")
    
    try:
        empresa = Empresa.objects.first()
        if not empresa:
            print_error("No hay empresas registradas")
            return
        
        series_data = [
            {'tipo': '01', 'serie': 'F001', 'nombre': 'Facturas'},
            {'tipo': '03', 'serie': 'B001', 'nombre': 'Boletas'},
            {'tipo': '07', 'serie': 'FC01', 'nombre': 'Notas de Crédito'},
            {'tipo': '08', 'serie': 'FD01', 'nombre': 'Notas de Débito'},
            {'tipo': '09', 'serie': 'T001', 'nombre': 'Guías de Remisión'},
        ]
        
        for serie_info in series_data:
            serie, created = SerieComprobante.objects.get_or_create(
                empresa=empresa,
                tipo_comprobante=serie_info['tipo'],
                serie=serie_info['serie'],
                defaults={
                    'numero_actual': 0,
                    'numero_maximo': 99999999,
                    'activa': True,
                    'punto_venta': 'PRINCIPAL'
                }
            )
            
            if created:
                print_success(f"Serie {serie_info['serie']} creada para {serie_info['nombre']}")
            else:
                print_info(f"Serie {serie_info['serie']} ya existe")
                
    except Exception as e:
        print_error(f"Error al crear series: {e}")

def mostrar_resumen_datos():
    """Mostrar resumen de datos cargados"""
    print_info("Resumen de datos cargados:")
    print(f"  📊 Empresas: {Empresa.objects.count()}")
    print(f"  👥 Clientes: {Cliente.objects.count()}")
    print(f"  📦 Productos: {Producto.objects.count()}")
    print(f"  👤 Usuarios: {Usuario.objects.count()}")
    print(f"  🧾 Series: {SerieComprobante.objects.count()}")
    print(f"  ⚙️  Configuraciones: {ConfiguracionSistema.objects.count()}")

def crear_usuario_admin():
    """Crear usuario administrador"""
    print_header("CREAR USUARIO ADMINISTRADOR")
    
    try:
        # Solicitar datos
        email = input("Email del administrador: ").strip()
        if not email:
            print_error("Email es requerido")
            return
        
        nombres = input("Nombres: ").strip()
        apellido_paterno = input("Apellido paterno: ").strip()
        apellido_materno = input("Apellido materno: ").strip()
        numero_documento = input("Número de documento: ").strip()
        
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(email=email).exists():
            print_error(f"Ya existe un usuario con el email {email}")
            return
        
        # Obtener empresa
        empresa = Empresa.objects.first()
        if not empresa:
            print_error("No hay empresas registradas. Cargue datos iniciales primero.")
            return
        
        # Crear usuario
        with transaction.atomic():
            usuario = Usuario.objects.create_superuser(
                email=email,
                password='admin123',  # Password por defecto
                username=email.split('@')[0],
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                numero_documento=numero_documento,
                empresa=empresa,
                is_staff=True,
                is_superuser=True,
                es_admin_empresa=True
            )
            
            print_success(f"Usuario administrador creado: {email}")
            print_warning("Password por defecto: admin123")
            print_info("Recuerde cambiar la contraseña en el primer login")
            
    except Exception as e:
        print_error(f"Error al crear usuario: {e}")

def hacer_backup():
    """Crear backup de la base de datos"""
    print_header("BACKUP DE BASE DE DATOS")
    
    try:
        # Generar nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_felicita_{timestamp}.sql"
        backup_path = os.path.join(settings.BASE_DIR, 'backups', backup_file)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Comando para backup
        db_config = settings.DATABASES['default']
        comando = [
            'pg_dump',
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--username={db_config['USER']}",
            f"--dbname={db_config['NAME']}",
            '--verbose',
            '--clean',
            '--no-owner',
            '--no-privileges',
            f"--file={backup_path}"
        ]
        
        # Configurar password
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        print_info(f"Creando backup en: {backup_path}")
        
        # Ejecutar comando
        result = subprocess.run(comando, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success(f"Backup creado exitosamente: {backup_file}")
            
            # Mostrar tamaño del archivo
            size = os.path.getsize(backup_path)
            size_mb = size / (1024 * 1024)
            print_info(f"Tamaño del backup: {size_mb:.2f} MB")
        else:
            print_error(f"Error al crear backup: {result.stderr}")
            
    except Exception as e:
        print_error(f"Error al hacer backup: {e}")

def limpiar_cache():
    """Limpiar cache del sistema"""
    print_header("LIMPIAR CACHE")
    
    try:
        cache.clear()
        print_success("Cache limpiado correctamente")
        
        # Limpiar cache de Django
        call_command('clearsessions')
        print_success("Sesiones expiradas eliminadas")
        
    except Exception as e:
        print_error(f"Error al limpiar cache: {e}")

def verificar_sistema():
    """Verificar estado del sistema"""
    print_header("VERIFICACIÓN DEL SISTEMA")
    
    try:
        # Verificar conexión a BD
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print_success("Conexión a base de datos: OK")
            else:
                print_error("Conexión a base de datos: ERROR")
        
        # Verificar cache
        try:
            cache.set('test_key', 'test_value', 30)
            if cache.get('test_key') == 'test_value':
                print_success("Cache Redis: OK")
                cache.delete('test_key')
            else:
                print_error("Cache Redis: ERROR")
        except Exception:
            print_error("Cache Redis: NO DISPONIBLE")
        
        # Verificar datos básicos
        if Empresa.objects.exists():
            print_success("Datos de empresa: OK")
        else:
            print_warning("No hay empresas registradas")
        
        if Usuario.objects.exists():
            print_success("Usuarios del sistema: OK")
        else:
            print_warning("No hay usuarios registrados")
        
        # Verificar configuraciones
        configs_requeridas = [
            'IGV_PORCENTAJE', 'MONEDA_BASE', 'METODO_INVENTARIO'
        ]
        
        configs_faltantes = []
        for config in configs_requeridas:
            if not ConfiguracionSistema.objects.filter(clave=config).exists():
                configs_faltantes.append(config)
        
        if configs_faltantes:
            print_warning(f"Configuraciones faltantes: {', '.join(configs_faltantes)}")
        else:
            print_success("Configuraciones del sistema: OK")
        
        # Verificar directorios
        directorios = [
            settings.MEDIA_ROOT,
            os.path.join(settings.BASE_DIR, 'logs'),
            os.path.join(settings.BASE_DIR, 'backups'),
        ]
        
        for directorio in directorios:
            if os.path.exists(directorio) and os.access(directorio, os.W_OK):
                print_success(f"Directorio {os.path.basename(directorio)}: OK")
            else:
                print_warning(f"Directorio {os.path.basename(directorio)}: NO ACCESIBLE")
        
    except Exception as e:
        print_error(f"Error en verificación: {e}")

def mostrar_estadisticas():
    """Mostrar estadísticas del sistema"""
    print_header("ESTADÍSTICAS DEL SISTEMA")
    
    try:
        # Estadísticas básicas
        print("📊 Datos Generales:")
        print(f"   Empresas registradas: {Empresa.objects.count()}")
        print(f"   Usuarios activos: {Usuario.objects.filter(is_active=True).count()}")
        print(f"   Clientes registrados: {Cliente.objects.count()}")
        print(f"   Productos activos: {Producto.objects.filter(activo=True).count()}")
        
        # Estadísticas de facturación (si existen facturas)
        try:
            from aplicaciones.facturacion.models import Factura
            total_facturas = Factura.objects.count()
            print(f"\n💰 Facturación:")
            print(f"   Total facturas emitidas: {total_facturas}")
            
            if total_facturas > 0:
                facturas_mes = Factura.objects.filter(
                    fecha_emision__month=datetime.now().month,
                    fecha_emision__year=datetime.now().year
                ).count()
                print(f"   Facturas este mes: {facturas_mes}")
                
        except Exception:
            print("\n💰 Facturación: Módulo no inicializado")
        
        # Estadísticas de inventario
        try:
            from aplicaciones.inventario.models import StockProducto
            productos_con_stock = StockProducto.objects.filter(
                cantidad_actual__gt=0
            ).count()
            print(f"\n📦 Inventario:")
            print(f"   Productos con stock: {productos_con_stock}")
            
        except Exception:
            print("\n📦 Inventario: Módulo no inicializado")
        
        # Espacio en disco
        import shutil
        total, used, free = shutil.disk_usage(settings.BASE_DIR)
        print(f"\n💾 Espacio en Disco:")
        print(f"   Total: {total // (2**30)} GB")
        print(f"   Usado: {used // (2**30)} GB")
        print(f"   Libre: {free // (2**30)} GB")
        
    except Exception as e:
        print_error(f"Error al obtener estadísticas: {e}")

def menu_principal():
    """Menú principal de utilidades"""
    while True:
        print_header("UTILIDADES FELICITA")
        print("Seleccione una opción:")
        print("1. 📊 Cargar datos iniciales")
        print("2. 👤 Crear usuario administrador")
        print("3. 💾 Hacer backup de BD")
        print("4. 🧹 Limpiar cache")
        print("5. 🔍 Verificar sistema")
        print("6. 📈 Mostrar estadísticas")
        print("7. 🚪 Salir")
        
        opcion = input(f"\n{Colors.YELLOW}Ingrese su opción (1-7): {Colors.ENDC}").strip()
        
        if opcion == '1':
            cargar_datos_iniciales()
        elif opcion == '2':
            crear_usuario_admin()
        elif opcion == '3':
            hacer_backup()
        elif opcion == '4':
            limpiar_cache()
        elif opcion == '5':
            verificar_sistema()
        elif opcion == '6':
            mostrar_estadisticas()
        elif opcion == '7':
            print_info("¡Hasta luego!")
            break
        else:
            print_error("Opción no válida. Intente nuevamente.")
        
        input(f"\n{Colors.CYAN}Presione Enter para continuar...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        # Verificar argumentos de línea de comandos
        if len(sys.argv) > 1:
            comando = sys.argv[1]
            
            if comando == 'cargar-datos':
                cargar_datos_iniciales()
            elif comando == 'crear-admin':
                crear_usuario_admin()
            elif comando == 'backup':
                hacer_backup()
            elif comando == 'limpiar-cache':
                limpiar_cache()
            elif comando == 'verificar':
                verificar_sistema()
            elif comando == 'estadisticas':
                mostrar_estadisticas()
            else:
                print_error(f"Comando no reconocido: {comando}")
                print_info("Comandos disponibles: cargar-datos, crear-admin, backup, limpiar-cache, verificar, estadisticas")
        else:
            # Mostrar menú interactivo
            menu_principal()
            
    except KeyboardInterrupt:
        print_warning("\nOperación cancelada por el usuario")
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)