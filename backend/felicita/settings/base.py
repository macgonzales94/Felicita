"""
Configuración base Django para FELICITA
Sistema de Facturación Electrónica para Perú
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config

# ==============================================
# CONFIGURACIÓN DE DIRECTORIOS
# ==============================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==============================================
# CONFIGURACIÓN DE SEGURIDAD
# ==============================================

SECRET_KEY = config('DJANGO_SECRET_KEY', default='clave-temporal-cambiar-en-produccion')

# ==============================================
# APLICACIONES DJANGO
# ==============================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Para formateo de números
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
    'drf_spectacular',
    'django_celery_beat',
]

FELICITA_APPS = [
    'aplicaciones.usuarios',
    'aplicaciones.empresas',
    'aplicaciones.clientes',
    'aplicaciones.productos',
    'aplicaciones.inventarios',
    'aplicaciones.facturacion',
    'aplicaciones.contabilidad',
    'aplicaciones.reportes',
    'aplicaciones.configuraciones',
    'aplicaciones.sunat',
    'aplicaciones.pos',  # Punto de Venta
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + FELICITA_APPS

# ==============================================
# MIDDLEWARE
# ==============================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

# ==============================================
# CONFIGURACIÓN DE URLs
# ==============================================

ROOT_URLCONF = 'felicita.urls'

# ==============================================
# CONFIGURACIÓN DE TEMPLATES
# ==============================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
        },
    },
]

# ==============================================
# CONFIGURACIÓN WSGI
# ==============================================

WSGI_APPLICATION = 'felicita.wsgi.application'

# ==============================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ==============================================

AUTH_USER_MODEL = 'usuarios.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
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
# CONFIGURACIÓN REST FRAMEWORK
# ==============================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
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
}

# ==============================================
# CONFIGURACIÓN JWT
# ==============================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=config('JWT_EXPIRATION_HOURS', default=24, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'felicita',
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ==============================================
# CONFIGURACIÓN API DOCUMENTATION
# ==============================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'FELICITA API',
    'DESCRIPTION': 'Sistema de Facturación Electrónica para Perú - API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'TAGS': [
        {'name': 'Autenticación', 'description': 'Endpoints de login y gestión de usuarios'},
        {'name': 'Clientes', 'description': 'Gestión de clientes y proveedores'},
        {'name': 'Productos', 'description': 'Catálogo de productos y servicios'},
        {'name': 'Inventarios', 'description': 'Control de stock y almacenes'},
        {'name': 'Facturación', 'description': 'Emisión de comprobantes electrónicos'},
        {'name': 'Contabilidad', 'description': 'Asientos contables y estados financieros'},
        {'name': 'Reportes', 'description': 'Reportes y analytics'},
        {'name': 'POS', 'description': 'Punto de venta'},
        {'name': 'SUNAT', 'description': 'Integración con SUNAT y Nubefact'},
    ],
}

# ==============================================
# CONFIGURACIÓN DE INTERNACIONALIZACIÓN
# ==============================================

LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('es', 'Español'),
    ('es-pe', 'Español (Perú)'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# ==============================================
# CONFIGURACIÓN DE ARCHIVOS
# ==============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de subida de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# ==============================================
# CONFIGURACIÓN ESPECÍFICA PERÚ
# ==============================================

# Formatos de número para Perú
NUMBER_GROUPING = 3
THOUSAND_SEPARATOR = ','
DECIMAL_SEPARATOR = '.'

# Formatos de fecha para Perú
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'
SHORT_DATE_FORMAT = 'd/m/Y'

# Moneda por defecto
DEFAULT_CURRENCY = 'PEN'

# ==============================================
# CONFIGURACIÓN DE CELERY (Tareas en Background)
# ==============================================

CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# ==============================================
# CONFIGURACIÓN DE LOGGING BASE
# ==============================================

LOG_LEVEL = config('LOG_LEVEL', default='INFO')

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

print("🏗️ Configuración base Django cargada para FELICITA")