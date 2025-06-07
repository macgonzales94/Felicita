"""
ASGI config for FELICITA project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import sys
from django.core.asgi import get_asgi_application

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar el módulo de settings por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felicita.configuracion.produccion')

try:
    # Inicializar Django ASGI application early para asegurar que apps estén cargadas
    django_asgi_app = get_asgi_application()
    
    # Aquí se pueden agregar más aplicaciones ASGI como WebSockets
    # from channels.routing import ProtocolTypeRouter, URLRouter
    # from channels.auth import AuthMiddlewareStack
    # import aplicaciones.core.routing
    
    application = django_asgi_app
    
    # Para futuras implementaciones de WebSockets:
    # application = ProtocolTypeRouter({
    #     "http": django_asgi_app,
    #     "websocket": AuthMiddlewareStack(
    #         URLRouter([
    #             # WebSocket routes aquí
    #         ])
    #     ),
    # })
    
    # Log de inicialización en producción
    if not os.environ.get('DEBUG', False):
        import logging
        logger = logging.getLogger('felicita')
        logger.info("🚀 FELICITA ASGI application initialized successfully")
        
except Exception as e:
    # Log del error
    import logging
    logging.error(f"❌ Error initializing FELICITA ASGI application: {e}")
    raise