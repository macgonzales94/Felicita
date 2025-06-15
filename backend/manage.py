#!/usr/bin/env python
"""
FELICITA - Django Management Script
Sistema de Facturación Electrónica para Perú

Django's command-line utility for administrative tasks.
"""

import os
import sys
import logging
from decouple import config

def main():
    """Run administrative tasks."""
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    logger = logging.getLogger('felicita.manage')
    
    # ===========================================
    # CONFIGURACIÓN DEL AMBIENTE
    # ===========================================
    
    # Determinar el ambiente
    environment = config('ENVIRONMENT', default='local').lower()
    
    # Configurar Django settings module según el ambiente
    if environment in ['production', 'prod', 'staging']:
        settings_module = 'config.settings.produccion'
    elif environment in ['testing', 'test']:
        settings_module = 'config.settings.testing'
    else:
        settings_module = 'config.settings.local'
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    
    logger.info(f"🔧 FELICITA Management - Ambiente: {environment.upper()}")
    logger.info(f"⚙️  Settings module: {settings_module}")
    
    # ===========================================
    # VALIDACIONES PRE-EJECUCIÓN
    # ===========================================
    
    def validate_environment():
        """Validar que el ambiente esté correctamente configurado"""
        try:
            # Verificar que Django esté instalado
            try:
                import django
                logger.info(f"✅ Django {django.get_version()} detectado")
            except ImportError as exc:
                logger.error("❌ Django no está instalado o no está disponible en el PYTHONPATH.")
                logger.error(f"Error: {exc}")
                sys.exit(1)
            
            # Verificar archivo .env en desarrollo
            if environment in ['local', 'development']:
                env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                if not os.path.exists(env_file):
                    logger.warning("⚠️  Archivo .env no encontrado. Usando valores por defecto.")
                else:
                    logger.info("✅ Archivo .env encontrado")
            
            # Verificar variables críticas en producción
            if environment in ['production', 'prod', 'staging']:
                required_vars = [
                    'SECRET_KEY',
                    'DB_PRODUCCION_NOMBRE',
                    'DB_PRODUCCION_USUARIO',
                    'DB_PRODUCCION_PASSWORD',
                ]
                
                missing_vars = []
                for var in required_vars:
                    if not config(var, default=None):
                        missing_vars.append(var)
                
                if missing_vars:
                    logger.error(f"❌ Variables de entorno faltantes en producción: {missing_vars}")
                    sys.exit(1)
                else:
                    logger.info("✅ Variables de entorno de producción verificadas")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en validación del ambiente: {e}")
            return False
    
    # Validar ambiente
    if not validate_environment():
        sys.exit(1)
    
    # ===========================================
    # COMANDOS PERSONALIZADOS
    # ===========================================
    
    def handle_custom_commands():
        """Manejar comandos personalizados de FELICITA"""
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            # Comando para inicializar datos
            if command == 'init_felicita':
                logger.info("🚀 Inicializando FELICITA...")
                
                # Secuencia de comandos para inicialización
                commands = [
                    ['makemigrations'],
                    ['migrate'],
                    ['collectstatic', '--noinput'],
                    ['loaddata', 'fixtures/datos_iniciales.json'],
                ]
                
                for cmd in commands:
                    logger.info(f"Ejecutando: python manage.py {' '.join(cmd)}")
                    try:
                        from django.core.management import execute_from_command_line
                        execute_from_command_line(['manage.py'] + cmd)
                    except Exception as e:
                        logger.error(f"❌ Error ejecutando {cmd}: {e}")
                        sys.exit(1)
                
                logger.info("✅ FELICITA inicializado correctamente")
                sys.exit(0)
            
            # Comando para cargar datos de ejemplo
            elif command == 'load_sample_data':
                logger.info("📊 Cargando datos de ejemplo...")
                
                fixtures = [
                    'fixtures/usuarios_iniciales.json',
                    'fixtures/plan_cuentas_pcge.json',
                    'fixtures/productos_ejemplo.json',
                    'fixtures/clientes_ejemplo.json',
                    'fixtures/series_comprobantes.json',
                ]
                
                for fixture in fixtures:
                    if os.path.exists(fixture):
                        logger.info(f"Cargando: {fixture}")
                        try:
                            from django.core.management import execute_from_command_line
                            execute_from_command_line(['manage.py', 'loaddata', fixture])
                        except Exception as e:
                            logger.warning(f"⚠️  Error cargando {fixture}: {e}")
                    else:
                        logger.warning(f"⚠️  Fixture no encontrado: {fixture}")
                
                logger.info("✅ Datos de ejemplo cargados")
                sys.exit(0)
            
            # Comando para reset completo (solo desarrollo)
            elif command == 'reset_dev':
                if environment not in ['local', 'development']:
                    logger.error("❌ El comando reset_dev solo está disponible en desarrollo")
                    sys.exit(1)
                
                logger.warning("⚠️  RESET COMPLETO - Se eliminarán todos los datos")
                
                import time
                logger.info("Esperando 5 segundos... (Ctrl+C para cancelar)")
                time.sleep(5)
                
                commands = [
                    ['flush', '--noinput'],
                    ['migrate'],
                    ['createsuperuser', '--noinput', '--username=admin', '--email=admin@felicita.pe'],
                    ['loaddata', 'fixtures/datos_iniciales.json'],
                ]
                
                for cmd in commands:
                    try:
                        from django.core.management import execute_from_command_line
                        execute_from_command_line(['manage.py'] + cmd)
                    except Exception as e:
                        logger.warning(f"⚠️  Error en {cmd}: {e}")
                
                logger.info("🔄 Reset de desarrollo completado")
                sys.exit(0)
            
            # Mostrar ayuda personalizada
            elif command == 'help_felicita':
                print("\n🇵🇪 FELICITA - Comandos Personalizados:")
                print("  init_felicita        - Inicializar sistema completo")
                print("  load_sample_data     - Cargar datos de ejemplo")
                print("  reset_dev           - Reset completo (solo desarrollo)")
                print("  help_felicita       - Mostrar esta ayuda")
                print("\n📘 Comandos Django estándar también disponibles:")
                print("  runserver           - Iniciar servidor de desarrollo")
                print("  shell              - Abrir shell de Django")
                print("  makemigrations     - Crear migraciones")
                print("  migrate            - Aplicar migraciones")
                print("  collectstatic      - Recolectar archivos estáticos")
                print("  createsuperuser    - Crear superusuario")
                print("  test               - Ejecutar tests")
                print()
                sys.exit(0)
    
    # Manejar comandos personalizados
    handle_custom_commands()
    
    # ===========================================
    # EJECUCIÓN PRINCIPAL
    # ===========================================
    
    try:
        from django.core.management import execute_from_command_line
        
        # Log del comando ejecutado (excepto runserver para evitar spam)
        if len(sys.argv) > 1 and sys.argv[1] != 'runserver':
            logger.info(f"🔧 Ejecutando comando: {' '.join(sys.argv[1:])}")
        
        # Ejecutar comando Django
        execute_from_command_line(sys.argv)
        
    except ImportError as exc:
        logger.error("❌ No se pudo importar Django.")
        logger.error("¿Está instalado y disponible en tu variable PYTHONPATH?")
        logger.error("¿Olvidaste activar el virtual environment?")
        logger.error(f"Error específico: {exc}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("\n⚡ Comando interrumpido por el usuario")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando comando: {e}")
        sys.exit(1)

# ===========================================
# INFORMACIÓN DEL SISTEMA
# ===========================================

def show_system_info():
    """Mostrar información del sistema"""
    if '--info' in sys.argv:
        import platform
        import django
        
        print("\n🔍 INFORMACIÓN DEL SISTEMA FELICITA:")
        print(f"  🐍 Python: {platform.python_version()}")
        
        try:
            print(f"  🔧 Django: {django.get_version()}")
        except:
            print("  🔧 Django: No instalado")
        
        print(f"  💻 Sistema: {platform.system()} {platform.release()}")
        print(f"  🏗️  Arquitectura: {platform.architecture()[0]}")
        print(f"  📁 Directorio: {os.getcwd()}")
        print(f"  🌍 Ambiente: {config('ENVIRONMENT', default='local').upper()}")
        print()
        sys.exit(0)

# Mostrar información si se solicita
show_system_info()

# ===========================================
# BANNER FELICITA
# ===========================================

def show_banner():
    """Mostrar banner de FELICITA"""
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print("\n" + "="*60)
        print("🇵🇪 FELICITA - Sistema de Facturación Electrónica para Perú")
        print("="*60)
        print(f"🌍 Ambiente: {config('ENVIRONMENT', default='local').upper()}")
        print("🚀 Iniciando servidor de desarrollo...")
        print("📱 Admin: http://localhost:8000/admin/")
        print("📖 API Docs: http://localhost:8000/api/docs/")
        print("="*60 + "\n")

# Mostrar banner para runserver
show_banner()

# ===========================================
# PUNTO DE ENTRADA
# ===========================================

if __name__ == '__main__':
    main()