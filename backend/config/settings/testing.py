"""
FELICITA - Configuración Testing Django
Sistema de Facturación Electrónica para Perú

Configuraciones específicas para testing y pruebas automatizadas
"""

from .base import *
import tempfile

# ===========================================
# CONFIGURACIÓN TESTING
# ===========================================

DEBUG = False
ENVIRONMENT = 'testing'

# Hosts para testing
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# ===========================================
# BASE DE DATOS TESTING
# ===========================================

# Usar base de datos en memoria para testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        },
        'TEST': {
            'NAME': ':memory:',
        }
    }
}

# ===========================================
# CACHE TESTING
# ===========================================

# Usar cache dummy para testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# ===========================================
# EMAIL TESTING
# ===========================================

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ===========================================
# ARCHIVOS MEDIA TESTING
# ===========================================

# Usar directorio temporal para media en testing
MEDIA_ROOT = tempfile.mkdtemp()

# ===========================================
# PASSWORD TESTING
# ===========================================

# Usar password hasher simple para testing (más rápido)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ===========================================
# LOGGING TESTING
# ===========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'CRITICAL',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'CRITICAL',
    },
}

# ===========================================
# MIDDLEWARE TESTING
# ===========================================

# Remover middleware innecesario para testing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ===========================================
# CORS TESTING
# ===========================================

CORS_ALLOW_ALL_ORIGINS = True

# ===========================================
# SEGURIDAD TESTING
# ===========================================

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# ===========================================
# CELERY TESTING
# ===========================================

# Ejecutar tareas síncronamente en testing
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# ===========================================
# INTEGRACIONES TESTING
# ===========================================

# Configuración mock para integraciones en testing
NUBEFACT_CONFIG.update({
    'mode': 'demo',
    'base_url': 'https://demo-api.nubefact.com/api/v1',
    'token': 'test_token',
    'ruc': '20123456789',
})

APIS_PERU_CONFIG.update({
    'reniec_url': 'http://test-reniec.api',
    'sunat_url': 'http://test-sunat.api',
    'reniec_token': 'test_reniec_token',
    'sunat_token': 'test_sunat_token',
})

# ===========================================
# CONFIGURACIÓN TESTING ESPECÍFICA
# ===========================================

# Desactivar migraciones para testing más rápido
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Configuración para tests paralelos
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Configuración para coverage
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]

# ===========================================
# FIXTURES TESTING
# ===========================================

# Usar fixtures específicas para testing
FIXTURE_DIRS = [
    BASE_DIR / 'fixtures' / 'testing',
    BASE_DIR / 'fixtures',
]

# ===========================================
# STATIC FILES TESTING
# ===========================================

# Usar collectfast para testing más rápido
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ===========================================
# REST FRAMEWORK TESTING
# ===========================================

REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
})

# ===========================================
# TIEMPO ZONES TESTING
# ===========================================

# Usar UTC para testing consistente
USE_TZ = True
TIME_ZONE = 'UTC'

# ===========================================
# EMPRESAS TESTING
# ===========================================

EMPRESA_CONFIG.update({
    'ruc': '20123456789',
    'razon_social': 'EMPRESA TEST SAC',
    'direccion': 'AV. TEST 123, LIMA, PERU',
    'telefono': '01-1234567',
    'email': 'test@felicita.pe',
})

# ===========================================
# CONFIGURACIÓN FACTORY BOY
# ===========================================

# Configuración para factory_boy
FACTORY_FOR_DJANGO_MODELS = True

# ===========================================
# PYTEST CONFIGURACIÓN
# ===========================================

# Configuración específica para pytest-django
PYTEST_SETTINGS = {
    'DJANGO_SETTINGS_MODULE': 'config.settings.testing',
    'addopts': [
        '--tb=short',
        '--strict-markers',
        '--disable-warnings',
        '--reuse-db',
    ],
}

print("🧪 FELICITA - Configuración TESTING cargada correctamente")
print(f"💾 Base de datos: {DATABASES['default']['ENGINE']} en memoria")
print(f"📧 Email Backend: {EMAIL_BACKEND}")
print(f"🔄 Cache Backend: {CACHES['default']['BACKEND']}")
print(f"📁 Media Root: {MEDIA_ROOT}")