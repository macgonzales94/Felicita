"""
FELICITA - WSGI Configuration
Sistema de Facturación Electrónica para Perú

WSGI config for FELICITA project.

Expone el callable WSGI como una variable a nivel de módulo llamada 'application'.

Para más información sobre este archivo, ver:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import logging
from django.core.wsgi import get_wsgi_application
from decouple import config

# Configurar logging temprano
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger('felicita.wsgi')

# ===========================================
# CONFIGURACIÓN DEL AMBIENTE
# ===========================================

# Determinar el ambiente
ENVIRONMENT = config('ENVIRONMENT', default='local').lower()

# Configurar Django settings module
if ENVIRONMENT in ['production', 'prod', 'staging']:
    settings_module = 'config.settings.produccion'
elif ENVIRONMENT in ['testing', 'test']:
    settings_module = 'config.settings.testing'
else:
    settings_module = 'config.settings.local'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

logger.info(f"🚀 FELICITA WSGI - Ambiente: {ENVIRONMENT.upper()}")
logger.info(f"⚙️  Settings module: {settings_module}")

# ===========================================
# CONFIGURACIÓN DEL PATH
# ===========================================

# Agregar el directorio del proyecto al Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logger.info(f"📁 Base directory: {BASE_DIR}")

# ===========================================
# APLICACIÓN WSGI
# ===========================================

try:
    # Obtener la aplicación WSGI
    application = get_wsgi_application()
    logger.info("✅ Aplicación WSGI creada exitosamente")
    
except Exception as e:
    logger.error(f"❌ Error al crear aplicación WSGI: {e}")
    raise

# ===========================================
# CONFIGURACIÓN PARA HOSTING COMPARTIDO
# ===========================================

def configure_shared_hosting():
    """Configuración específica para hosting compartido"""
    try:
        # Configuraciones típicas para cPanel/hosting compartido
        import django
        from django.conf import settings
        
        django.setup()
        
        # Log de configuración
        logger.info("🏠 Configuración para hosting compartido aplicada")
        logger.info(f"🗄️  Base de datos: {settings.DATABASES['default']['ENGINE']}")
        logger.info(f"🔧 Debug mode: {settings.DEBUG}")
        logger.info(f"🌐 Allowed hosts: {settings.ALLOWED_HOSTS}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en configuración de hosting compartido: {e}")
        return False

# Aplicar configuración para hosting compartido en producción
if ENVIRONMENT in ['production', 'prod', 'staging']:
    configure_shared_hosting()

# ===========================================
# MIDDLEWARE PERSONALIZADO WSGI
# ===========================================

class FelicitaWSGIMiddleware:
    """Middleware WSGI personalizado para FELICITA"""
    
    def __init__(self, application):
        self.application = application
        
    def __call__(self, environ, start_response):
        # Agregar headers personalizados
        def new_start_response(status, response_headers, exc_info=None):
            # Headers de seguridad
            response_headers.append(('X-Powered-By', 'FELICITA-Peru'))
            response_headers.append(('X-Content-Type-Options', 'nosniff'))
            response_headers.append(('X-Frame-Options', 'DENY'))
            response_headers.append(('X-XSS-Protection', '1; mode=block'))
            
            # Header de versión
            response_headers.append(('X-FELICITA-Version', '1.0.0'))
            
            return start_response(status, response_headers, exc_info)
        
        # Log de request (solo en desarrollo)
        if ENVIRONMENT not in ['production', 'prod', 'staging']:
            method = environ.get('REQUEST_METHOD', 'GET')
            path = environ.get('PATH_INFO', '/')
            logger.debug(f"📥 {method} {path}")
        
        return self.application(environ, new_start_response)

# Aplicar middleware personalizado
application = FelicitaWSGIMiddleware(application)

# ===========================================
# MANEJO DE ERRORES WSGI
# ===========================================

def handle_wsgi_error(environ, start_response):
    """Manejo de errores a nivel WSGI"""
    try:
        return application(environ, start_response)
    except Exception as e:
        logger.error(f"❌ Error WSGI no manejado: {e}")
        
        # Respuesta de error simple
        status = '500 Internal Server Error'
        headers = [
            ('Content-Type', 'application/json'),
            ('X-FELICITA-Error', 'WSGI-Handler'),
        ]
        
        error_response = {
            'error': 'Internal Server Error',
            'message': 'Ocurrió un error interno del servidor.',
            'timestamp': str(timezone.now()),
        }
        
        import json
        response_body = json.dumps(error_response).encode('utf-8')
        
        start_response(status, headers)
        return [response_body]

# Solo usar manejo de errores en producción
if ENVIRONMENT in ['production', 'prod', 'staging']:
    application = handle_wsgi_error

# ===========================================
# VALIDACIONES FINALES
# ===========================================

def validate_wsgi_config():
    """Validar configuración WSGI"""
    try:
        import django
        from django.conf import settings
        
        # Verificar configuración Django
        if not settings.configured:
            logger.error("❌ Django settings no configurado")
            return False
        
        # Verificar base de datos en producción
        if ENVIRONMENT in ['production', 'prod', 'staging']:
            db_config = settings.DATABASES['default']
            required_db_settings = ['NAME', 'USER', 'PASSWORD', 'HOST']
            
            for setting in required_db_settings:
                if not db_config.get(setting):
                    logger.error(f"❌ Configuración de BD faltante: {setting}")
                    return False
        
        logger.info("✅ Configuración WSGI validada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en validación WSGI: {e}")
        return False

# Validar configuración
if not validate_wsgi_config():
    logger.warning("⚠️  Advertencias en configuración WSGI")

logger.info("🎯 FELICITA WSGI configurado y listo")

# ===========================================
# INFORMACIÓN DEL SISTEMA
# ===========================================

try:
    import platform
    import django
    
    logger.info("📊 Información del sistema:")
    logger.info(f"  🐍 Python: {platform.python_version()}")
    logger.info(f"  🔧 Django: {django.get_version()}")
    logger.info(f"  💻 Sistema: {platform.system()} {platform.release()}")
    logger.info(f"  🏗️  Arquitectura: {platform.architecture()[0]}")
    
except Exception as e:
    logger.warning(f"⚠️  No se pudo obtener información del sistema: {e}")

# ===========================================
# EXPORT PARA GUNICORN/UWSGI
# ===========================================

# Para compatibilidad con diferentes servidores WSGI
app = application  # Alias para Gunicorn
wsgi_application = application  # Alias para otros servidores