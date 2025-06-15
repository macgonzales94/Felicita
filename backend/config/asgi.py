"""
FELICITA - ASGI Configuration
Sistema de Facturación Electrónica para Perú

ASGI config for FELICITA project.

Expone el callable ASGI como una variable a nivel de módulo llamada 'application'.

Para más información sobre este archivo, ver:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import sys
import logging
from django.core.asgi import get_asgi_application
from decouple import config

# Configurar logging temprano
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger('felicita.asgi')

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

logger.info(f"🚀 FELICITA ASGI - Ambiente: {ENVIRONMENT.upper()}")
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
# APLICACIÓN ASGI
# ===========================================

try:
    # Obtener la aplicación ASGI Django
    django_asgi_app = get_asgi_application()
    logger.info("✅ Aplicación ASGI Django creada exitosamente")
    
except Exception as e:
    logger.error(f"❌ Error al crear aplicación ASGI Django: {e}")
    raise

# ===========================================
# ROUTING ASGI PARA FUTURAS FUNCIONALIDADES
# ===========================================

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# URL patterns para WebSockets (futuro)
websocket_urlpatterns = [
    # Aquí se agregarán las rutas WebSocket en el futuro
    # path('ws/notifications/', NotificationConsumer.as_asgi()),
    # path('ws/pos/', POSConsumer.as_asgi()),
    # path('ws/reports/', ReportsConsumer.as_asgi()),
]

# ===========================================
# APLICACIÓN ASGI COMPLETA
# ===========================================

application = ProtocolTypeRouter({
    # HTTP requests van a Django
    "http": django_asgi_app,
    
    # WebSocket connections (futuro)
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(websocket_urlpatterns)
    # ),
})

logger.info("🌐 Aplicación ASGI configurada (HTTP ready, WebSocket preparado para futuro)")

# ===========================================
# MIDDLEWARE ASGI PERSONALIZADO
# ===========================================

class FelicitaASGIMiddleware:
    """Middleware ASGI personalizado para FELICITA"""
    
    def __init__(self, inner):
        self.inner = inner
        
    async def __call__(self, scope, receive, send):
        # Agregar información personalizada al scope
        scope['felicita'] = {
            'version': '1.0.0',
            'ambiente': ENVIRONMENT,
            'timestamp': self.get_timestamp(),
        }
        
        # Log de conexiones WebSocket (futuro)
        if scope['type'] == 'websocket':
            logger.info(f"🔌 Nueva conexión WebSocket: {scope.get('path', '/')}")
        
        # Log de requests HTTP (solo en desarrollo)
        elif scope['type'] == 'http' and ENVIRONMENT not in ['production', 'prod']:
            method = scope.get('method', 'GET')
            path = scope.get('path', '/')
            logger.debug(f"📥 {method} {path}")
        
        return await self.inner(scope, receive, send)
    
    def get_timestamp(self):
        """Obtener timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()

# Aplicar middleware personalizado
application = FelicitaASGIMiddleware(application)

# ===========================================
# MANEJO DE ERRORES ASGI
# ===========================================

class ASGIErrorHandler:
    """Manejo de errores ASGI"""
    
    def __init__(self, inner):
        self.inner = inner
        
    async def __call__(self, scope, receive, send):
        try:
            return await self.inner(scope, receive, send)
        except Exception as e:
            logger.error(f"❌ Error ASGI no manejado: {e}")
            
            # Solo manejar errores HTTP
            if scope['type'] == 'http':
                await self.send_error_response(send, e)
            else:
                # Para WebSocket, cerrar la conexión
                await send({
                    'type': 'websocket.close',
                    'code': 1011  # Internal Error
                })
    
    async def send_error_response(self, send, error):
        """Enviar respuesta de error HTTP"""
        import json
        from datetime import datetime
        
        error_response = {
            'error': 'Internal Server Error',
            'message': 'Ocurrió un error interno del servidor.',
            'timestamp': datetime.now().isoformat(),
        }
        
        # Solo incluir detalles del error en desarrollo
        if ENVIRONMENT not in ['production', 'prod', 'staging']:
            error_response['detail'] = str(error)
        
        response_body = json.dumps(error_response).encode('utf-8')
        
        await send({
            'type': 'http.response.start',
            'status': 500,
            'headers': [
                [b'content-type', b'application/json'],
                [b'x-felicita-error', b'asgi-handler'],
            ],
        })
        
        await send({
            'type': 'http.response.body',
            'body': response_body,
        })

# Solo usar manejo de errores en producción
if ENVIRONMENT in ['production', 'prod', 'staging']:
    application = ASGIErrorHandler(application)

# ===========================================
# CONFIGURACIONES PARA WEBSOCKETS (FUTURO)
# ===========================================

# Redis para channel layers (cuando se implementen WebSockets)
REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/2')

# Configuración para Channels (futuro)
CHANNEL_LAYERS_CONFIG = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'prefix': 'felicita_channels',
        },
    },
}

logger.info(f"🔄 Redis configurado para channels: {REDIS_URL}")

# ===========================================
# VALIDACIONES ASGI
# ===========================================

def validate_asgi_config():
    """Validar configuración ASGI"""
    try:
        import django
        from django.conf import settings
        
        # Verificar configuración Django
        if not settings.configured:
            logger.error("❌ Django settings no configurado para ASGI")
            return False
        
        # Verificar que ASGI esté habilitado
        if not hasattr(settings, 'ASGI_APPLICATION'):
            logger.info("ℹ️  ASGI_APPLICATION no configurado (usando ASGI básico)")
        
        logger.info("✅ Configuración ASGI validada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en validación ASGI: {e}")
        return False

# Validar configuración
validate_asgi_config()

# ===========================================
# INFORMACIÓN ASGI
# ===========================================

logger.info("🎯 FELICITA ASGI configurado y listo")
logger.info("📡 Protocolos soportados:")
logger.info("  ✅ HTTP/1.1")
logger.info("  ✅ HTTP/2 (si el servidor lo soporta)")
logger.info("  🔄 WebSocket (preparado para futuro)")

# ===========================================
# EXPORT PARA UVICORN/HYPERCORN
# ===========================================

# Para compatibilidad con diferentes servidores ASGI
app = application  # Alias para Uvicorn
asgi_application = application  # Alias para otros servidores

# ===========================================
# COMANDOS DE EJECUCIÓN
# ===========================================

# Documentar comandos para diferentes servidores ASGI
ASGI_COMMANDS = {
    'uvicorn': 'uvicorn config.asgi:application --host 0.0.0.0 --port 8000',
    'hypercorn': 'hypercorn config.asgi:application --bind 0.0.0.0:8000',
    'daphne': 'daphne -b 0.0.0.0 -p 8000 config.asgi:application',
}

logger.info("🚀 Comandos ASGI disponibles:")
for server, command in ASGI_COMMANDS.items():
    logger.info(f"  {server}: {command}")

# ===========================================
# NOTAS PARA DESARROLLO FUTURO
# ===========================================

"""
NOTAS PARA IMPLEMENTACIÓN FUTURA DE WEBSOCKETS:

1. Notificaciones en tiempo real:
   - Estados de facturación
   - Alertas de stock
   - Notificaciones del sistema

2. Punto de venta en tiempo real:
   - Sincronización entre dispositivos
   - Actualizaciones de inventario
   - Estado de caja

3. Reportes en tiempo real:
   - Dashboard actualizado automáticamente
   - Gráficos dinámicos
   - Alertas de negocio

4. Colaboración:
   - Múltiples usuarios editando
   - Chat de soporte
   - Notificaciones de equipo

Para implementar:
1. pip install channels channels-redis
2. Agregar 'channels' a INSTALLED_APPS
3. Configurar CHANNEL_LAYERS en settings
4. Crear consumers para WebSocket
5. Definir routing patterns
6. Actualizar este archivo ASGI
"""