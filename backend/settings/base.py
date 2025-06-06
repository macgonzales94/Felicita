"""
Configuración base completa de Django para FELICITA
Sistema de Facturación Electrónica para Perú
FASE 2: Configuración de Seguridad y Autenticación Completa
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# ==============================================
# CONFIGURACIÓN BASE DEL PROYECTO
# ==============================================

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('DJANGO_SECRET_KEY', default='clave-super-secreta-felicita-2024-cambiar-en-produccion')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='local')

# Hosts permitidos
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0', cast=Csv())

# ==============================================
# APLICACIONES DJANGO
# ==============================================

# Aplicaciones de Django
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

# Aplicaciones de terceros
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

# Aplicaciones locales de FELICITA
LOCAL_APPS = [
    'aplicaciones.empresas',
    'aplicaciones.usuarios',
    # Próximas fases
    # 'aplicaciones.facturacion',
    # 'aplicaciones.contabilidad', 
    # 'aplicaciones.inventarios',
    # 'aplicaciones.productos',
    # 'aplicaciones.clientes',
    # 'aplicaciones.pos',
    # 'aplicaciones.reportes',
    # 'aplicaciones.configuraciones',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ==============================================
# MIDDLEWARE DE SEGURIDAD FELICITA
# ==============================================

MIDDLEWARE = [
    # CORS debe ir primero
    'corsheaders.middleware.CorsMiddleware',
    
    # Middleware de seguridad de FELICITA
    'aplicaciones.usuarios.middleware.SeguridadFelicitaMiddleware',
    'aplicaciones.usuarios.middleware.BloqueoIntentosFallidosMiddleware',
    
    # Middleware estándar de Django
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Middleware adicional de FELICITA después de autenticación
    'aplicaciones.usuarios.middleware.AutenticacionJWTMiddleware',
    'aplicaciones.usuarios.middleware.AuditoriaMiddleware',
    
    # Middleware estándar restante
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    
    # Monitoreo de rendimiento al final
    'aplicaciones.usuarios.middleware.MonitoreoRendimientoMiddleware',
]

# ==============================================
# CONFIGURACIÓN DE URLs Y WSGI
# ==============================================

ROOT_URLCONF = 'felicita.urls'
WSGI_APPLICATION = 'felicita.wsgi.application'

# ==============================================
# TEMPLATES
# ==============================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==============================================
# BASE DE DATOS
# ==============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME', default='felicita_db'),
        'USER': config('DATABASE_USER', default='felicita_user'),
        'PASSWORD': config('DATABASE_PASSWORD', default='felicita_password'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
        'OPTIONS': {
            'options': '-c default_transaction_isolation=serializable'
        },
        'CONN_MAX_AGE': 600,
    }
}

# ==============================================
# CONFIGURACIÓN DE CACHE (Redis)
# ==============================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'felicita',
        'TIMEOUT': 300,  # 5 minutos por defecto
    }
}

# ==============================================
# MODELO DE USUARIO PERSONALIZADO
# ==============================================

AUTH_USER_MODEL = 'usuarios.Usuario'

# ==============================================
# CONFIGURACIÓN REST FRAMEWORK CON SEGURIDAD
# ==============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'aplicaciones.usuarios.permissions.PermisosEmpresa',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'aplicaciones.usuarios.utils.custom_exception_handler',
    
    # Configuración de throttling para seguridad
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/min',
        'user': '100/min',
        'login': '5/min',
    },
    
    # Configuración de metadatos
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    
    # Configuración de parsers
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
}

# ==============================================
# CONFIGURACIÓN JWT COMPLETA
# ==============================================

SIMPLE_JWT = {
    # Duración de tokens
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=config('REFRESH_TOKEN_LIFETIME_HOURS', default=24, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    # Configuración de algoritmo y claves
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'FELICITA',
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    # Configuración de headers
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    # Claims
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    
    # Configuración de sliding tokens (no usado)
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ==============================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'first_name', 'last_name', 'email'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================
# CONFIGURACIÓN CORS
# ==============================================

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)

CORS_ALLOWED_HEADERS = [
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
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# ==============================================
# CONFIGURACIÓN DE INTERNACIONALIZACIÓN
# ==============================================

LANGUAGE_CODE = 'es-pe'
TIME_ZONE = config('TIME_ZONE', default='America/Lima')
USE_I18N = True
USE_TZ = True

# Idiomas disponibles
LANGUAGES = [
    ('es', 'Español'),
    ('es-pe', 'Español (Perú)'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# ==============================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==============================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media')

# Tamaño máximo de upload
DATA_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE', default=10485760, cast=int)  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE', default=10485760, cast=int)  # 10MB

# ==============================================
# CONFIGURACIÓN DEFAULT AUTO FIELD
# ==============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================
# CONFIGURACIÓN DE EMAIL
# ==============================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@felicita.pe')

# ==============================================
# CONFIGURACIÓN DE LOGGING
# ==============================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'felicita': {
            'format': '[FELICITA] {asctime} - {levelname} - {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'felicita',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'felicita.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='INFO'),
        },
        'felicita': {
            'handlers': ['console', 'file'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'security': {
            'handlers': ['console', 'security_file'],
            'level': config('SECURITY_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'aplicaciones.usuarios': {
            'handlers': ['console', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
logs_dir = BASE_DIR / 'logs'
logs_dir.mkdir(exist_ok=True)

# ==============================================
# CONFIGURACIÓN SPECTACULAR (OpenAPI/Swagger)
# ==============================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'FELICITA API',
    'DESCRIPTION': 'Sistema de Facturación Electrónica para Perú - API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'DEFAULT_GENERATOR_CLASS': 'drf_spectacular.generators.SchemaGenerator',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVERS': [
        {
            'url': 'http://localhost:8000',
            'description': 'Servidor de Desarrollo Local'
        },
    ],
    'TAGS': [
        {'name': 'auth', 'description': 'Autenticación y gestión de usuarios'},
        {'name': 'empresas', 'description': 'Gestión de empresas'},
        {'name': 'facturacion', 'description': 'Facturación electrónica'},
        {'name': 'contabilidad', 'description': 'Contabilidad y asientos'},
        {'name': 'inventarios', 'description': 'Control de inventarios'},
        {'name': 'productos', 'description': 'Catálogo de productos'},
        {'name': 'clientes', 'description': 'Gestión de clientes'},
        {'name': 'pos', 'description': 'Punto de venta'},
        {'name': 'reportes', 'description': 'Reportes y analytics'},
    ],
    'CONTACT': {
        'name': 'Equipo FELICITA',
        'email': 'soporte@felicita.pe',
    },
    'LICENSE': {
        'name': 'Propietario',
    },
}

# ==============================================
# CONFIGURACIONES DE SEGURIDAD FELICITA
# ==============================================

# Configuración de autenticación y seguridad
MAX_INTENTOS_LOGIN = config('MAX_INTENTOS_LOGIN', default=5, cast=int)
TIEMPO_BLOQUEO_MINUTOS = config('TIEMPO_BLOQUEO_MINUTOS', default=15, cast=int)
SESSION_TIMEOUT_MINUTES = config('SESSION_TIMEOUT_MINUTES', default=120, cast=int)

# Rate limiting
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_PER_MINUTE = config('RATELIMIT_PER_MINUTE', default=60, cast=int)

# Configuración de logging de seguridad
SECURITY_LOG_LEVEL = config('SECURITY_LOG_LEVEL', default='INFO')
AUDIT_LOG_RETENTION_DAYS = config('AUDIT_LOG_RETENTION_DAYS', default=365, cast=int)

# Configuración de tokens
TOKEN_LIFETIME_MINUTES = config('TOKEN_LIFETIME_MINUTES', default=60, cast=int)
REFRESH_TOKEN_LIFETIME_HOURS = config('REFRESH_TOKEN_LIFETIME_HOURS', default=24, cast=int)

# Configuración de sesiones concurrentes
ALLOW_CONCURRENT_SESSIONS = config('ALLOW_CONCURRENT_SESSIONS', default=True, cast=bool)
MAX_CONCURRENT_SESSIONS = config('MAX_CONCURRENT_SESSIONS', default=3, cast=int)

# Configuración de notificaciones de seguridad
SEND_SECURITY_NOTIFICATIONS = config('SEND_SECURITY_NOTIFICATIONS', default=True, cast=bool)
SECURITY_EMAIL_RECIPIENTS = config('SECURITY_EMAIL_RECIPIENTS', default='admin@felicita.pe').split(',')

# URLs del frontend para notificaciones
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')
FRONTEND_LOGIN_URL = config('FRONTEND_LOGIN_URL', default=f'{FRONTEND_URL}/login')

# ==============================================
# CONFIGURACIONES ESPECÍFICAS FELICITA
# ==============================================

# Configuración de facturas
FACTURA_CONFIG = {
    'NUMERACION_AUTOMATICA': True,
    'PERMITIR_CERO_STOCK': False,
    'METODO_COSTEO': 'PEPS',  # Obligatorio SUNAT
    'CALCULO_IGV_AUTOMATICO': True,
    'IGV_INCLUIDO_EN_PRECIOS': False,
}

# Configuración de reportes
REPORTE_CONFIG = {
    'FORMATO_FECHA_DEFECTO': 'dd/mm/yyyy',
    'EXPORTAR_EXCEL_PERMITIDO': True,
    'EXPORTAR_PDF_PERMITIDO': True,
    'LIMITE_REGISTROS_EXCEL': 10000,
}

# Configuración de inventarios
INVENTARIO_CONFIG = {
    'ALERTAS_STOCK_MINIMO': True,
    'STOCK_NEGATIVO_PERMITIDO': False,
    'REDONDEO_DECIMALES': 2,
    'METODO_VALUACION': 'PEPS',
}

# Configuración Nubefact
NUBEFACT_CONFIG = {
    'TOKEN': config('NUBEFACT_TOKEN', default=''),
    'RUC': config('NUBEFACT_RUC', default='20123456789'),
    'USUARIO_SOL': config('NUBEFACT_USUARIO_SOL', default='MODDATOS'),
    'CLAVE_SOL': config('NUBEFACT_CLAVE_SOL', default='MODDATOS'),
    'MODE': config('NUBEFACT_MODE', default='demo'),
    'BASE_URL': config('NUBEFACT_BASE_URL', default='https://demo-ose.nubefact.com/ol-ti-itcpe/billService'),
}

# Configuración SUNAT
SUNAT_CONFIG = {
    'IGV_RATE': config('IGV_RATE', default=0.18, cast=float),
    'MONEDA_NACIONAL': config('MONEDA_NACIONAL', default='PEN'),
    'CONSULTA_RUC_URL': config('SUNAT_CONSULTA_RUC_URL', default='https://api.sunat.gob.pe/v1/contribuyente/contribuyentes/'),
}

# APIs Externas
APIS_EXTERNAS = {
    'RENIEC_TOKEN': config('RENIEC_TOKEN', default=''),
    'SUNAT_TOKEN': config('SUNAT_TOKEN', default=''),
}

print("🔧 Configuración base Django cargada para FELICITA - FASE 2 COMPLETA")