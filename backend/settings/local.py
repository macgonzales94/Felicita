"""
Configuración para desarrollo local de FELICITA
Sistema de Facturación Electrónica para Perú
FASE 2: Configuración optimizada para desarrollo con seguridad
"""

from .base import *
from datetime import timedelta

# ==============================================
# CONFIGURACIÓN DE DESARROLLO
# ==============================================

DEBUG = True
ENVIRONMENT = 'local'

# Hosts permitidos para desarrollo
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '[::1]']

# ==============================================
# BASE DE DATOS LOCAL (PostgreSQL en Docker)
# ==============================================

DATABASES['default'].update({
    'NAME': config('DATABASE_NAME', default='felicita_db'),
    'USER': config('DATABASE_USER', default='felicita_user'),
    'PASSWORD': config('DATABASE_PASSWORD', default='felicita_password_2024'),
    'HOST': config('DATABASE_HOST', default='localhost'),
    'PORT': config('DATABASE_PORT', default='5432'),
    'OPTIONS': {
        'options': '-c default_transaction_isolation=serializable'
    },
    'CONN_MAX_AGE': 0,  # No persistent connections en desarrollo
})

# ==============================================
# CACHE REDIS LOCAL
# ==============================================

CACHES['default'].update({
    'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
    'TIMEOUT': 300,
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
    },
})

# ==============================================
# CONFIGURACIÓN DE AUTENTICACIÓN Y SEGURIDAD LOCAL
# ==============================================

# JWT para desarrollo (configuración extendida)
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),  # Token más largo para desarrollo
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    # Claims personalizados
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    # Configuración de tokens
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    
    # Configuración de algoritmo
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'FELICITA',
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
})

# ==============================================
# CONFIGURACIONES DE SEGURIDAD PARA DESARROLLO
# ==============================================

# Configuración de intentos de login (más permisiva para desarrollo)
MAX_INTENTOS_LOGIN = config('MAX_INTENTOS_LOGIN', default=10, cast=int)
TIEMPO_BLOQUEO_MINUTOS = config('TIEMPO_BLOQUEO_MINUTOS', default=5, cast=int)
SESSION_TIMEOUT_MINUTES = config('SESSION_TIMEOUT_MINUTES', default=480, cast=int)  # 8 horas

# Rate limiting (más permisivo para desarrollo)
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_PER_MINUTE = config('RATELIMIT_PER_MINUTE', default=200, cast=int)

# Configuración de logs de seguridad
SECURITY_LOG_LEVEL = 'DEBUG'
AUDIT_LOG_RETENTION_DAYS = 30  # Menor retención en desarrollo

# Configuración de sesiones concurrentes
ALLOW_CONCURRENT_SESSIONS = True
MAX_CONCURRENT_SESSIONS = 10  # Más sesiones permitidas en desarrollo

# Configuración de notificaciones (deshabilitadas en desarrollo)
SEND_SECURITY_NOTIFICATIONS = False
SECURITY_EMAIL_RECIPIENTS = ['admin@felicita.pe']

# URLs del frontend
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
FRONTEND_LOGIN_URL = f'{FRONTEND_URL}/login'

# ==============================================
# CORS PARA DESARROLLO
# ==============================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_ALL_ORIGINS = False  # Solo para desarrollo controlado
CORS_ALLOW_CREDENTIALS = True

# Headers adicionales para desarrollo
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-forwarded-for',
    'x-forwarded-proto',
    'x-debug-mode',  # Header personalizado para desarrollo
]

# ==============================================
# EMAIL PARA DESARROLLO
# ==============================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Si quieres probar email real, descomenta y configura:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ==============================================
# CONFIGURACIÓN DE LOGGING PARA DESARROLLO
# ==============================================

LOGGING['loggers'].update({
    'django': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    'django.db.backends': {
        'handlers': ['console'],
        'level': 'DEBUG' if config('SHOW_SQL_QUERIES', default=False, cast=bool) else 'INFO',
        'propagate': False,
    },
    'felicita': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'aplicaciones': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
})

# ==============================================
# CONFIGURACIÓN DE DEBUGGING
# ==============================================

# Django Debug Toolbar (si está instalado)
if 'debug_toolbar' in INSTALLED_APPS:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', '::1']
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_COLLAPSED': True,
        'DISABLE_PANELS': [
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ],
    }

# ==============================================
# CONFIGURACIÓN NUBEFACT PARA DESARROLLO
# ==============================================

NUBEFACT_CONFIG.update({
    'MODE': 'demo',  # Siempre demo en desarrollo
    'TOKEN': config('NUBEFACT_TOKEN', default='test_token_demo'),
    'RUC': config('NUBEFACT_RUC', default='20123456789'),
    'USUARIO_SOL': config('NUBEFACT_USUARIO_SOL', default='MODDATOS'),
    'CLAVE_SOL': config('NUBEFACT_CLAVE_SOL', default='MODDATOS'),
    'BASE_URL': 'https://demo-ose.nubefact.com/ol-ti-itcpe/billService',
    'TIMEOUT': 30,  # Mayor timeout para desarrollo
    'RETRY_ATTEMPTS': 3,
})

# ==============================================
# CONFIGURACIÓN DE DATOS DEMO
# ==============================================

# Empresa por defecto para desarrollo
EMPRESA_DEMO = {
    'RUC': config('EMPRESA_RUC', default='20123456789'),
    'RAZON_SOCIAL': config('EMPRESA_RAZON_SOCIAL', default='EMPRESA DEMO FELICITA S.A.C.'),
    'DIRECCION': config('EMPRESA_DIRECCION', default='Av. Lima 123, Lima, Lima, Perú'),
    'TELEFONO': config('EMPRESA_TELEFONO', default='+51 1 234-5678'),
    'EMAIL': config('EMPRESA_EMAIL', default='demo@felicita.pe'),
}

# ==============================================
# CONFIGURACIÓN DE ARCHIVOS PARA DESARROLLO
# ==============================================

# Archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files con mayor límite para desarrollo
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB para desarrollo
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB para desarrollo

# ==============================================
# CONFIGURACIÓN REST FRAMEWORK DESARROLLO
# ==============================================

# Configuración más permisiva para desarrollo
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # UI navegable para desarrollo
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/min',      # Más permisivo para desarrollo
        'user': '200/min',     # Más permisivo para desarrollo
        'login': '10/min',     # Más intentos de login
    },
})

# ==============================================
# CONFIGURACIÓN SPECTACULAR PARA DESARROLLO
# ==============================================

SPECTACULAR_SETTINGS.update({
    'SERVE_INCLUDE_SCHEMA': True,  # Incluir schema en desarrollo
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVERS': [
        {
            'url': 'http://localhost:8000',
            'description': 'Servidor de Desarrollo Local'
        },
        {
            'url': 'http://127.0.0.1:8000',
            'description': 'Servidor de Desarrollo Local (127.0.0.1)'
        },
    ],
    'SCHEMA_PATH_PREFIX': '/api/',
    'DEFAULT_GENERATOR_CLASS': 'drf_spectacular.generators.SchemaGenerator',
})

# ==============================================
# CONFIGURACIONES ADICIONALES DESARROLLO
# ==============================================

# Configuración de timezone para desarrollo
USE_TZ = True
TIME_ZONE = 'America/Lima'

# Configuración de idioma
LANGUAGE_CODE = 'es-pe'
USE_I18N = True
USE_L10N = True

# Configuración de formatos de fecha/hora para Perú
DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Formato de números para Perú
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
DECIMAL_SEPARATOR = '.'

# ==============================================
# CONFIGURACIÓN DE DESARROLLO ESPECÍFICA
# ==============================================

# Hot reload automático
DEVELOPMENT_SETTINGS = {
    'AUTO_RELOAD': True,
    'SHOW_EXCEPTION_DETAILS': True,
    'ENABLE_PROFILING': config('ENABLE_PROFILING', default=False, cast=bool),
    'MOCK_EXTERNAL_APIS': config('MOCK_EXTERNAL_APIS', default=True, cast=bool),
}

# Configuración de testing
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_DATABASE_PREFIX = 'test_'

# Configuración de sesiones para desarrollo
SESSION_COOKIE_AGE = 86400 * 7  # 7 días
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ==============================================
# IMPRESIÓN DE CONFIGURACIÓN PARA DESARROLLO
# ==============================================

print("🏗️ Configuración local de desarrollo cargada para FELICITA")
print(f"🔧 Entorno: {ENVIRONMENT}")
print(f"🐘 Base de datos: {DATABASES['default']['NAME']} en {DATABASES['default']['HOST']}")
print(f"🔑 Cache Redis: {CACHES['default']['LOCATION']}")
print(f"🌐 CORS permitido para: {', '.join(CORS_ALLOWED_ORIGINS)}")
print(f"🔐 JWT lifetime: {SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']}")
print(f"⚡ Rate limit: {RATELIMIT_PER_MINUTE} req/min")
print(f"🚀 Frontend URL: {FRONTEND_URL}")
print("✅ Configuración de desarrollo lista para FELICITA FASE 2")

# ==============================================
# ADVERTENCIAS DE DESARROLLO
# ==============================================

if DEBUG:
    import warnings
    warnings.filterwarnings('ignore', message='Django is running in DEBUG mode')
    
    print("\n" + "="*50)
    print("🚨 MODO DESARROLLO ACTIVADO")
    print("="*50)
    print("⚠️  No usar esta configuración en producción")
    print("⚠️  Los logs de seguridad están en modo DEBUG")
    print("⚠️  Rate limiting reducido para desarrollo")
    print("⚠️  Tokens JWT con mayor duración")
    print("⚠️  CORS configurado para localhost solamente")
    print("="*50)

# Variables de entorno requeridas para desarrollo
REQUIRED_ENV_VARS = [
    'DATABASE_NAME',
    'DATABASE_USER', 
    'DATABASE_PASSWORD',
    'JWT_SECRET_KEY',
]

missing_vars = [var for var in REQUIRED_ENV_VARS if not config(var, default=None)]
if missing_vars:
    print(f"\n❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
    print("💡 Revisa tu archivo .env")
else:
    print("\n✅ Todas las variables de entorno requeridas están configuradas")