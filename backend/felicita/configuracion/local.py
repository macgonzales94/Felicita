"""
CONFIGURACIÓN LOCAL - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Configuración para desarrollo local con Nubefact DEMO
"""

from .base import *
import os

# =============================================================================
# CONFIGURACIÓN DE DESARROLLO
# =============================================================================
DEBUG = True

# Base de datos PostgreSQL local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'felicita_db'),
        'USER': os.getenv('POSTGRES_USER', 'felicita_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'felicita123'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'charset': 'utf8',
        },
        'TEST': {
            'NAME': 'test_felicita_db',
        },
    }
}

# CORS para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Media y Static files para desarrollo
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# =============================================================================
# CONFIGURACIÓN NUBEFACT DEMO
# =============================================================================
NUBEFACT_CONFIG = {
    # Configuración para ambiente DEMO/TEST
    'token': os.getenv('NUBEFACT_TOKEN_DEMO', 'test_token_demo'),
    'ruc': '20000000001',  # RUC de prueba para desarrollo
    'usuario_sol': 'TESTUSER',
    'clave_sol': 'TESTPASS',
    
    # URLs Nubefact
    'base_url': 'https://api.nubefact.com/api/v1/',
    'demo_url': 'https://demo.nubefact.com/api/v1/',
    'webhook_url': f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/integraciones/webhook/",
    
    # Configuración de ambiente
    'modo': 'demo',  # 'demo' o 'produccion'
    'debug': True,
    
    # Configuración de comprobantes
    'series': {
        'factura': 'F001',
        'boleta': 'B001',
        'nota_credito': 'FC01',
        'nota_debito': 'FD01',
    },
    
    # Configuración de timeouts
    'timeout_conexion': 30,
    'max_reintentos': 3,
    'delay_reintentos': 5,
    
    # Configuración de logs
    'log_requests': True,
    'log_responses': True,
    'log_errors': True,
}

# =============================================================================
# CONFIGURACIÓN SUNAT PARA DESARROLLO
# =============================================================================
SUNAT_CONFIG = {
    'ruc_empresa': NUBEFACT_CONFIG['ruc'],
    'razon_social': 'EMPRESA DE PRUEBA FELICITA S.A.C.',
    'nombre_comercial': 'FELICITA DEMO',
    'direccion': 'AV. DEMO 123 - LIMA',
    'ubigeo': '150101',  # Lima
    
    # IGV Perú
    'igv_tasa': 0.18,
    'igv_codigo': '1000',  # Código IGV SUNAT
    
    # Moneda por defecto
    'moneda_default': 'PEN',
    
    # Validaciones automáticas
    'validar_ruc': True,
    'validar_correlatividad': True,
    'validar_totales': True,
}

# =============================================================================
# CONFIGURACIÓN REDIS PARA CACHE
# =============================================================================
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'felicita_dev',
        'TIMEOUT': 300,  # 5 minutos por defecto
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 horas

# =============================================================================
# CONFIGURACIÓN CELERY PARA TAREAS ASÍNCRONAS
# =============================================================================
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')

CELERY_TASK_ROUTES = {
    'aplicaciones.integraciones.tasks.enviar_nubefact': {'queue': 'nubefact'},
    'aplicaciones.inventario.tasks.actualizar_stock': {'queue': 'inventario'},
    'aplicaciones.contabilidad.tasks.generar_asiento': {'queue': 'contabilidad'},
}

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'America/Lima'

# =============================================================================
# CONFIGURACIÓN DE LOGGING EXTENDIDA
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
            'datefmt': '%H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR.parent, 'logs', 'felicita_dev.log'),
            'formatter': 'verbose'
        },
        'nubefact': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler', 
            'filename': os.path.join(BASE_DIR.parent, 'logs', 'nubefact.log'),
            'formatter': 'verbose'
        },
        'inventario': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR.parent, 'logs', 'inventario.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'felicita': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'felicita.nubefact': {
            'handlers': ['console', 'nubefact'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'felicita.inventario': {
            'handlers': ['console', 'inventario'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'felicita.facturacion': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS Y MEDIA
# =============================================================================
# Directorios para archivos generados
COMPROBANTES_DIR = os.path.join(MEDIA_ROOT, 'comprobantes')
REPORTES_DIR = os.path.join(MEDIA_ROOT, 'reportes')
TEMP_DIR = os.path.join(MEDIA_ROOT, 'temp')

# Crear directorios si no existen
for directory in [COMPROBANTES_DIR, REPORTES_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuración de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# =============================================================================
# CONFIGURACIÓN DE EMAIL PARA DESARROLLO
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = 'noreply@felicita.pe'
ADMIN_EMAIL = 'admin@felicita.pe'

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD PARA DESARROLLO
# =============================================================================
# Relajar configuraciones para desarrollo
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# JWT Settings específicos para desarrollo
from datetime import timedelta

SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # 24 horas en desarrollo
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # 7 días en desarrollo
    'ROTATE_REFRESH_TOKENS': True,
})

# =============================================================================
# CONFIGURACIÓN ESPECÍFICA DE APPS
# =============================================================================

# Configuración de inventario
INVENTARIO_CONFIG = {
    'metodo_valuacion': 'PEPS',  # Obligatorio en Perú
    'control_lotes': True,
    'alertas_stock_minimo': True,
    'actualizacion_automatica': True,
}

# Configuración de contabilidad
CONTABILIDAD_CONFIG = {
    'plan_cuentas': 'PCGE',  # Plan Contable General Empresarial
    'asientos_automaticos': True,
    'validar_balance': True,
    'periodo_contable_actual': 2024,
}

# Configuración de reportes
REPORTES_CONFIG = {
    'formatos_disponibles': ['PDF', 'EXCEL', 'CSV'],
    'reportes_automaticos': True,
    'envio_email': False,  # Deshabilitado en desarrollo
}

# =============================================================================
# CONFIGURACIÓN DE DEBUG TOOLBAR (OPCIONAL)
# =============================================================================
if DEBUG:
    try:
        import debug_toolbar
        
        INSTALLED_APPS += [
            'debug_toolbar',
        ]
        
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        
        INTERNAL_IPS = [
            '127.0.0.1',
            'localhost',
        ]
        
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TEMPLATE_CONTEXT': True,
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }
        
    except ImportError:
        pass

# =============================================================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# =============================================================================
# Cargar variables adicionales para desarrollo
ENVIRONMENT = 'development'
APP_VERSION = '1.0.0-dev'

# Configuración de URLs
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Configuración de webhooks
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'felicita_webhook_secret_dev')

print("🚀 FELICITA configurado para DESARROLLO LOCAL")
print(f"📊 Base de datos: {DATABASES['default']['NAME']}")
print(f"🔧 Nubefact: {NUBEFACT_CONFIG['modo']}")
print(f"💾 Redis: {REDIS_URL}")
print(f"📧 Email: {EMAIL_BACKEND}")
print("=" * 50)