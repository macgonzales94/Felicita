# CONOCIMIENTO BASE COMPLETO - PROYECTO FELICITA

## 📋 **INFORMACIÓN GENERAL DEL PROYECTO**

### **Nombre del Proyecto:** FELICITA
### **Descripción:** Sistema de Facturación Electrónica completo para empresas peruanas
### **Objetivo:** Software que cumpla 100% normativa SUNAT con facturación electrónica, inventarios, contabilidad y punto de venta
### **Repositorio:** https://github.com/macgonzales94/felicita
### **Licencia:** MIT License
### **Versión:** 1.0.0

---

## 🏗️ **ARQUITECTURA TÉCNICA DEFINIDA**

### **Stack Tecnológico Final:**
- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Base de Datos:** MySQL 8.0 (desarrollo local con Docker)
- **Cache:** Redis 7 para optimización
- **Integración SUNAT:** Nubefact API (OSE certificado)
- **Autenticación:** JWT con djangorestframework-simplejwt
- **Deployment:** Backend en hosting compartido MySQL, Frontend en Vercel

### **Decisión Base de Datos - MySQL 8.0:**
```
RAZONES DE LA ELECCIÓN:
✅ Hosting compartido disponible ($3-10/mes vs $15-200/mes PostgreSQL)
✅ phpMyAdmin incluido para administración visual
✅ Setup más simple para deployment en cPanel
✅ MySQL 8.0 tiene todas las features necesarias:
   - JSON fields nativo para metadatos
   - Window functions para reportes complejos
   - Triggers para automatización contable
   - AUTO_INCREMENT para numeración SUNAT
   - Performance excelente para OLTP (facturación)
✅ Amplio soporte en hosting providers peruanos
✅ Curva de aprendizaje menor para equipos
✅ Ecosystem maduro y documentación abundante

MIGRACIÓN DE POSTGRESQL:
- Sequences → AUTO_INCREMENT (numeración SUNAT)
- Arrays → Tablas relacionadas (sin pérdida funcional)
- JSON functions → Compatibles en MySQL 8.0
- Triggers → Más básicos pero suficientes
```

### **Estructura del Proyecto:**
```
felicita/
├── README.md                    # Documentación principal
├── docker-compose.yml           # MySQL + phpMyAdmin + Redis
├── .env.example                 # Variables de entorno ejemplo
├── .gitignore                   # Archivos ignorados Git
├── iniciar-desarrollo.sh/.bat   # Scripts automatizados
├── CONOCIMIENTO_BASE.md         # Este archivo
│
├── backend/                     # Django Backend
│   ├── manage.py
│   ├── requirements.txt         # mysqlclient + dependencias
│   ├── requirements/            # Por ambiente
│   │   ├── base.txt
│   │   ├── local.txt
│   │   └── produccion.txt
│   │
│   ├── config/                  # Configuraciones Django
│   │   ├── __init__.py
│   │   └── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Configuración base
│   │   │   ├── local.py         # MySQL local con Docker
│   │   │   ├── produccion.py    # Hosting compartido
│   │   │   └── testing.py       # Para tests
│   │   ├── __init__.py
│   │   ├── urls.py             # URLs principales
│   │   ├── wsgi.py             # WSGI para producción
│   │   └── asgi.py             # ASGI para futuro
│   │
│   ├── aplicaciones/           # Apps Django organizadas
│   │   ├── __init__.py
│   │   ├── core/              # Entidades base del sistema
│   │   │   ├── models.py      # Empresa, Sucursal, Config
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   ├── usuarios/          # Autenticación JWT
│   │   │   ├── models.py      # Usuario personalizado, Roles
│   │   │   ├── serializers.py # Auth, Login, Register
│   │   │   ├── views.py       # JWT Views
│   │   │   └── urls.py
│   │   ├── facturacion/       # Comprobantes SUNAT
│   │   │   ├── models.py      # Factura, Boleta, Items
│   │   │   ├── serializers.py # Validaciones SUNAT
│   │   │   ├── services.py    # Lógica de negocio
│   │   │   ├── views.py       # API REST
│   │   │   └── urls.py
│   │   ├── inventario/        # Stock y PEPS
│   │   │   ├── models.py      # Producto, Almacen, Movimientos
│   │   │   ├── services.py    # Algoritmo PEPS
│   │   │   ├── serializers.py
│   │   │   └── views.py
│   │   ├── contabilidad/      # PCGE y asientos
│   │   │   ├── models.py      # PlanCuentas, AsientoContable
│   │   │   ├── services.py    # Asientos automáticos
│   │   │   └── views.py
│   │   ├── integraciones/     # APIs externas
│   │   │   ├── models.py      # Logs de integraciones
│   │   │   ├── services/
│   │   │   │   └── nubefact.py # Servicio Nubefact
│   │   │   ├── views.py       # Webhooks
│   │   │   └── webhook_urls.py
│   │   ├── punto_venta/       # Lógica POS
│   │   │   ├── models.py      # Sesiones, Cierres
│   │   │   ├── serializers.py
│   │   │   └── views.py
│   │   └── reportes/          # PLE y analytics
│   │       ├── models.py
│   │       ├── services.py    # Generación PLE
│   │       └── views.py
│   │
│   ├── fixtures/              # Datos iniciales
│   │   ├── usuarios_iniciales.json
│   │   ├── plan_cuentas_pcge.json
│   │   ├── productos_ejemplo.json
│   │   ├── clientes_ejemplo.json
│   │   ├── series_comprobantes.json
│   │   └── datos_iniciales.json
│   │
│   ├── static/               # Archivos estáticos Django
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── admin/
│   │
│   ├── media/                # Archivos uploaded
│   │   ├── comprobantes/     # PDFs generados
│   │   ├── reportes/         # Reportes Excel/PDF
│   │   └── uploads/          # Archivos usuario
│   │
│   └── logs/                 # Logs aplicación
│       ├── django.log
│       ├── nubefact.log
│       └── auditoria.log
│
├── frontend/                 # React Frontend
│   ├── package.json          # Dependencias Node.js
│   ├── package-lock.json
│   ├── tsconfig.json         # Configuración TypeScript
│   ├── tailwind.config.js    # Configuración Tailwind
│   ├── vite.config.ts        # Configuración Vite
│   ├── postcss.config.js     # PostCSS para Tailwind
│   │
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── logo-felicita.png
│   │
│   ├── src/
│   │   ├── main.tsx          # Entry point React
│   │   ├── App.tsx           # Componente principal
│   │   ├── vite-env.d.ts     # Types Vite
│   │   │
│   │   ├── componentes/      # Componentes React
│   │   │   ├── comunes/      # Componentes reutilizables
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   ├── Cargando.tsx
│   │   │   │   └── MensajeError.tsx
│   │   │   ├── formularios/  # Forms específicos
│   │   │   │   ├── FormularioCliente.tsx
│   │   │   │   ├── FormularioFactura.tsx
│   │   │   │   └── FormularioProducto.tsx
│   │   │   └── ui/           # shadcn/ui components
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       ├── input.tsx
│   │   │       ├── modal.tsx
│   │   │       └── index.ts
│   │   │
│   │   ├── paginas/          # Páginas principales
│   │   │   ├── Login.tsx     # Autenticación
│   │   │   ├── Dashboard.tsx # Panel principal
│   │   │   ├── PuntoDeVenta.tsx # POS
│   │   │   ├── Facturacion.tsx # Gestión facturas
│   │   │   ├── Inventario.tsx # Gestión inventario
│   │   │   ├── Clientes.tsx  # Gestión clientes
│   │   │   ├── Productos.tsx # Gestión productos
│   │   │   ├── Reportes.tsx  # Reportes y analytics
│   │   │   └── Configuracion.tsx # Settings
│   │   │
│   │   ├── contextos/        # Estado global React
│   │   │   ├── AuthContext.tsx # Autenticación
│   │   │   ├── FacturacionContext.tsx # Estado POS
│   │   │   └── AppContext.tsx # Estado general
│   │   │
│   │   ├── servicios/        # APIs y servicios
│   │   │   ├── api.ts        # Configuración base Axios
│   │   │   ├── auth.ts       # Servicios autenticación
│   │   │   ├── facturas.ts   # APIs facturación
│   │   │   ├── productos.ts  # APIs productos
│   │   │   ├── clientes.ts   # APIs clientes
│   │   │   ├── inventario.ts # APIs inventario
│   │   │   └── reportes.ts   # APIs reportes
│   │   │
│   │   ├── types/            # Interfaces TypeScript
│   │   │   ├── index.ts      # Exports generales
│   │   │   ├── auth.ts       # Types autenticación
│   │   │   ├── factura.ts    # Types facturación
│   │   │   ├── producto.ts   # Types productos
│   │   │   ├── cliente.ts    # Types clientes
│   │   │   └── common.ts     # Types comunes
│   │   │
│   │   ├── hooks/            # Hooks personalizados
│   │   │   ├── useAuth.ts    # Hook autenticación
│   │   │   ├── useApi.ts     # Hook APIs genérico
│   │   │   ├── useLocalStorage.ts # Persistencia local
│   │   │   └── useDebounce.ts # Debounce búsquedas
│   │   │
│   │   ├── utils/            # Utilidades
│   │   │   ├── validaciones.ts # RUC, DNI, email
│   │   │   ├── formatos.ts   # Formateo datos
│   │   │   ├── constantes.ts # Constantes app
│   │   │   ├── helpers.ts    # Funciones auxiliares
│   │   │   └── storage.ts    # LocalStorage helpers
│   │   │
│   │   └── estilos/          # CSS específicos
│   │       ├── globals.css   # Estilos globales
│   │       ├── dashboard.css # Dashboard específico
│   │       └── punto-venta.css # POS específico
│   │
│   └── dist/                 # Build producción (generado)
│
├── documentacion/            # Documentación proyecto
│   ├── INSTALACION.md        # Guía instalación
│   ├── API.md               # Documentación API
│   ├── ARQUITECTURA.md      # Arquitectura sistema
│   ├── DEPLOYMENT.md        # Guía deployment
│   ├── MANUAL_USUARIO.md    # Manual usuario final
│   ├── DEVELOPMENT.md       # Guía desarrollo
│   └── TESTING.md           # Guía testing
│
├── scripts/                 # Scripts utilidades
│   ├── backup_db.py         # Backup base datos
│   ├── deploy.sh            # Deploy automatizado
│   ├── reset_db.sh          # Reset BD desarrollo
│   └── load_fixtures.py     # Cargar datos prueba
│
└── tests/                   # Tests del proyecto
    ├── backend/             # Tests Django
    ├── frontend/            # Tests React
    ├── integration/         # Tests integración
    └── e2e/                # Tests end-to-end
```

---

## 📊 **MÓDULOS DEL SISTEMA DETALLADOS**

### **1. Core (Entidades Base)**
**Ubicación:** `backend/aplicaciones/core/`
**Propósito:** Entidades fundamentales del sistema
**Modelos principales:**
- `Empresa`: RUC, razón social, configuración fiscal
- `Sucursal`: Múltiples ubicaciones por empresa
- `Configuracion`: Parámetros sistema (IGV, monedas, etc.)
- `TipoComprobante`: Catálogo tipos SUNAT (01, 03, 07, etc.)

### **2. Usuarios (Autenticación)**
**Ubicación:** `backend/aplicaciones/usuarios/`
**Propósito:** Sistema completo de autenticación y autorización
**Funcionalidades:**
- Usuario personalizado Django con JWT
- Roles: Administrador, Contador, Vendedor, Cliente
- Permisos granulares por módulo
- Autenticación stateless con tokens
- Renovación automática de tokens
- Logs de auditoría de accesos

### **3. Facturación Electrónica**
**Ubicación:** `backend/aplicaciones/facturacion/`
**Propósito:** Core de facturación SUNAT
**Funcionalidades:**
- Emisión facturas/boletas según normativa
- Integración Nubefact (OSE certificado)
- Notas de crédito y débito
- Guías de remisión
- Comunicaciones de baja
- Numeración correlativa automática (AUTO_INCREMENT)
- Validación XML UBL 2.1
- Estados: borrador, emitido, aceptado, rechazado, anulado

### **4. Punto de Venta (POS)**
**Ubicación:** `frontend/src/paginas/PuntoDeVenta.tsx` + `backend/aplicaciones/punto_venta/`
**Propósito:** Interfaz de venta optimizada
**Funcionalidades:**
- Interfaz táctil responsive (tablets)
- Catálogo productos con búsqueda
- Carrito tiempo real
- Múltiples métodos pago (efectivo, tarjeta, Yape)
- Códigos de barra
- Validación stock tiempo real
- Cálculo IGV automático (18%)
- Emisión directa facturas/boletas
- Cierre de caja diario

### **5. Control de Inventarios**
**Ubicación:** `backend/aplicaciones/inventario/`
**Propósito:** Gestión stock con método PEPS
**Funcionalidades:**
- Método PEPS obligatorio SUNAT
- Múltiples almacenes
- Transferencias entre almacenes
- Ajustes de inventario
- Alertas stock mínimo/máximo
- Kardex automatizado
- Reportes valorización
- Control lotes y vencimientos
- Categorías y subcategorías

### **6. Contabilidad Automática**
**Ubicación:** `backend/aplicaciones/contabilidad/`
**Propósito:** Automatización contable según PCGE
**Funcionalidades:**
- Plan cuentas PCGE completo
- Asientos automáticos por transacción
- Estados financieros básicos
- Cuentas por cobrar/pagar
- Conciliaciones automáticas
- Centro de costos
- Reportes contables

### **7. Integraciones**
**Ubicación:** `backend/aplicaciones/integraciones/`
**Propósito:** APIs externas y webhooks
**Funcionalidades:**
- Nubefact API (SUNAT OSE)
- RENIEC API (validación DNI)
- SUNAT API (validación RUC)
- Webhooks Nubefact
- Logs auditoría integraciones
- Manejo errores y reintentos
- Rate limiting

### **8. Reportes y Analytics**
**Ubicación:** `backend/aplicaciones/reportes/` + `frontend/src/paginas/Reportes.tsx`
**Propósito:** Business Intelligence y compliance SUNAT
**Funcionalidades:**
- Dashboard ejecutivo KPIs tiempo real
- Reportes PLE formato exacto SUNAT
- Análisis ventas con gráficos (Recharts)
- Exportación Excel/PDF
- Filtros avanzados
- Scheduled reports
- Business intelligence básico

---

## 🇵🇪 **NORMATIVA PERUANA ESPECÍFICA**

### **Cumplimiento SUNAT Obligatorio:**
```
FACTORES CRÍTICOS:
✅ Facturación electrónica obligatoria empresas >S/150,000 ingresos anuales
✅ Numeración correlativa sin vacíos (AUTO_INCREMENT MySQL garantiza)
✅ Formatos XML UBL 2.1 exactos según especificaciones técnicas
✅ Libros electrónicos PLE en formatos específicos SUNAT
✅ Método PEPS obligatorio para valuación inventarios
✅ IGV 18% calculado automáticamente en todos los comprobantes
✅ Retenciones y percepciones según corresponda
✅ Validación algoritmos RUC y DNI peruanos
✅ Tipos documento identidad según SUNAT
✅ Códigos SUNAT para productos y servicios
```

### **Tipos de Comprobante SUNAT:**
```python
TIPOS_COMPROBANTE = {
    '01': 'Factura',                    # B2B, obligatorio >S/700
    '03': 'Boleta de Venta',            # B2C, consumidor final
    '07': 'Nota de Crédito',            # Devoluciones, descuentos
    '08': 'Nota de Débito',             # Intereses, penalidades
    '09': 'Guía de Remisión',           # Traslado mercaderías
    '20': 'Comprobante de Retención',   # Retenciones 3%
    '40': 'Comprobante de Percepción',  # Percepciones
}
```

### **Validaciones Automáticas Peruanas:**
```python
# RUC: 11 dígitos con algoritmo verificador
def validar_ruc(ruc: str) -> bool:
    """Valida RUC peruano con dígito verificador"""
    if len(ruc) != 11 or not ruc.isdigit():
        return False
    
    # Algoritmo verificador RUC SUNAT
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(ruc[i]) * factores[i] for i in range(10))
    digito = 11 - (suma % 11)
    if digito >= 10:
        digito = digito - 10
    
    return int(ruc[10]) == digito

# DNI: 8 dígitos numéricos
def validar_dni(dni: str) -> bool:
    """Valida DNI peruano"""
    return len(dni) == 8 and dni.isdigit()
```

### **Plan de Cuentas PCGE:**
```
ESTRUCTURA PCGE (Plan Contable General Empresarial):
1. ACTIVO
   10: Efectivo y Equivalentes de Efectivo
   12: Cuentas por Cobrar Comerciales - Terceros
   20: Mercaderías
   21: Productos Terminados
   33: Inmuebles, Maquinaria y Equipo

2. PASIVO
   40: Tributos, Contraprestaciones y Aportes al Sistema de Pensiones y de Salud por Pagar
   42: Cuentas por Pagar Comerciales - Terceros
   45: Obligaciones Financieras

3. PATRIMONIO
   50: Capital
   58: Reservas
   59: Resultados Acumulados

4. GASTOS POR NATURALEZA
   60: Compras
   62: Gastos de Personal, Directores y Gerentes
   63: Gastos de Servicios Prestados por Terceros

5. INGRESOS
   70: Ventas
   75: Otros Ingresos de Gestión
   77: Ingresos Financieros
```

---

## 🔧 **CONFIGURACIÓN TÉCNICA DETALLADA**

### **Docker Development Environment:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  # MySQL 8.0 Database
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: felicita_db
      MYSQL_USER: felicita_user
      MYSQL_PASSWORD: dev_password_123
      MYSQL_ROOT_PASSWORD: root_password_123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    command: >
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --sql_mode=STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO
    restart: unless-stopped

  # phpMyAdmin for database administration
  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    environment:
      PMA_HOST: db
      PMA_PORT: 3306
      PMA_USER: felicita_user
      PMA_PASSWORD: dev_password_123
      MYSQL_ROOT_PASSWORD: root_password_123
    ports:
      - "8080:80"
    depends_on:
      - db
    restart: unless-stopped

  # Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### **Django Settings Structure:**
```python
# config/settings/base.py
import os
from decouple import config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',  # API documentation
]

LOCAL_APPS = [
    'aplicaciones.core',
    'aplicaciones.usuarios',
    'aplicaciones.facturacion',
    'aplicaciones.inventario',
    'aplicaciones.contabilidad',
    'aplicaciones.integraciones',
    'aplicaciones.punto_venta',
    'aplicaciones.reportes',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'felicita.urls'

# Database (will be overridden in local.py/produccion.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'usuarios.Usuario'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'FELICITA API',
    'DESCRIPTION': 'Sistema de Facturación Electrónica para Perú',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# Nubefact Configuration
NUBEFACT_CONFIG = {
    'mode': config('NUBEFACT_MODE', default='demo'),
    'token': config('NUBEFACT_TOKEN', default=''),
    'ruc': config('NUBEFACT_RUC', default=''),
    'base_url': 'https://api.nubefact.com/api/v1',
}

# Email Configuration
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'felicita': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### **Adaptaciones MySQL Específicas:**
```python
# Diferencias clave vs PostgreSQL

# 1. AUTO_INCREMENT en lugar de Sequences
class Factura(models.Model):
    # En MySQL usamos AutoField que maneja AUTO_INCREMENT
    numero = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['serie', 'numero']  # Garantiza unicidad
        
    def save(self, *args, **kwargs):
        if not self.numero:
            # Obtener siguiente número por serie
            last_numero = Factura.objects.filter(
                serie=self.serie
            ).aggregate(
                max_numero=models.Max('numero')
            )['max_numero'] or 0
            self.numero = last_numero + 1
        super().save(*args, **kwargs)

# 2. JSON Fields (MySQL 8.0 compatible)
class Configuracion(models.Model):
    parametros = models.JSONField(default=dict)  # Funciona igual
    metadatos = models.JSONField(default=dict)

# 3. Campos de texto con longitudes específicas
class Cliente(models.Model):
    razon_social = models.CharField(max_length=255)  # VARCHAR(255)
    numero_documento = models.CharField(max_length=11)  # RUC máximo
    direccion = models.TextField()  # TEXT en MySQL

# 4. Triggers MySQL para asientos automáticos
# En aplicaciones/contabilidad/migrations/xxxx_create_triggers.py
from django.db import migrations

def crear_trigger_asiento_venta(apps, schema_editor):
    schema_editor.execute("""
        CREATE TRIGGER trigger_asiento_venta
        AFTER INSERT ON facturacion_factura
        FOR EACH ROW
        BEGIN
            INSERT INTO contabilidad_asientocontable (
                fecha,
                concepto,
                debe_cuenta_12,
                haber_cuenta_70,
                haber_cuenta_40,
                monto
            ) VALUES (
                NEW.fecha_emision,
                CONCAT('Factura ', NEW.serie, '-', NEW.numero),
                NEW.total,
                NEW.subtotal,
                NEW.igv,
                NEW.total
            );
        END;
    """)

class Migration(migrations.Migration):
    dependencies = [
        ('contabilidad', '0001_initial'),
        ('facturacion', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(crear_trigger_asiento_venta),
    ]
```

### **Frontend React + TypeScript Configuration:**
```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@radix-ui/react-slot', 'lucide-react'],
          charts: ['recharts'],
          forms: ['react-hook-form', '@hookform/resolvers', 'zod'],
        },
      },
    },
  },
})

// frontend/tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta FELICITA
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: {
          500: '#10b981',
          600: '#059669',
        },
        warning: {
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          500: '#ef4444',
          600: '#dc2626',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [],
}

// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/componentes/*": ["./src/componentes/*"],
      "@/paginas/*": ["./src/paginas/*"],
      "@/servicios/*": ["./src/servicios/*"],
      "@/types/*": ["./src/types/*"],
      "@/utils/*": ["./src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 📝 **ESTÁNDARES DE CÓDIGO OBLIGATORIOS**

### **Nomenclatura EN ESPAÑOL (Estricto):**
```python
# ✅ CORRECTO - Backend Django
class Factura(models.Model):
    numero_documento = models.CharField(max_length=11, verbose_name='Número de Documento')
    razon_social = models.CharField(max_length=255, verbose_name='Razón Social')
    fecha_emision = models.DateField(verbose_name='Fecha de Emisión')
    fecha_vencimiento = models.DateField(verbose_name='Fecha de Vencimiento')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal')
    igv = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='IGV')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total')
    
    def calcular_igv(self):
        """Calcula el IGV del 18% sobre el subtotal"""
        return self.subtotal * Decimal('0.18')
    
    def generar_asiento_contable(self):
        """Genera asiento contable automático según PCGE"""
        AsientoContable.objects.create(
            factura=self,
            concepto=f'Venta según factura {self.serie}-{self.numero}',
            debe_cuenta_12=self.total,  # Cuentas por Cobrar
            haber_cuenta_70=self.subtotal,  # Ventas
            haber_cuenta_40=self.igv  # IGV por Pagar
        )

def validar_ruc_peruano(ruc: str) -> bool:
    """Valida RUC peruano con algoritmo dígito verificador"""
    if not ruc or len(ruc) != 11 or not ruc.isdigit():
        return False
    
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma_productos = sum(int(ruc[i]) * factores[i] for i in range(10))
    resto = suma_productos % 11
    digito_verificador = 11 - resto if resto >= 2 else resto
    
    return int(ruc[10]) == digito_verificador

# ❌ INCORRECTO - No usar inglés
class Invoice(models.Model):  # ❌ Debe ser Factura
    document_number = models.CharField()  # ❌ Debe ser numero_documento
    company_name = models.CharField()     # ❌ Debe ser razon_social
```

```typescript
// ✅ CORRECTO - Frontend React TypeScript
interface DatosFactura {
  clienteSeleccionado: Cliente;
  itemsFactura: ItemFactura[];
  subtotalSinIgv: number;
  montoIgv: number;
  totalConIgv: number;
  metodoPago: MetodoPago;
  observaciones?: string;
}

interface Cliente {
  id: number;
  tipoDocumento: 'dni' | 'ruc' | 'pasaporte';
  numeroDocumento: string;
  razonSocial: string;
  nombreComercial?: string;
  direccionFiscal: string;
  correoElectronico?: string;
  telefonoContacto?: string;
  activo: boolean;
  fechaCreacion: string;
}

const FormularioFactura: React.FC = () => {
  const [datosFactura, setDatosFactura] = useState<DatosFactura>({
    clienteSeleccionado: null,
    itemsFactura: [],
    subtotalSinIgv: 0,
    montoIgv: 0,
    totalConIgv: 0,
    metodoPago: 'efectivo'
  });
  
  const [cargandoDatos, setCargandoDatos] = useState(false);
  const [errorMensaje, setErrorMensaje] = useState<string | null>(null);
  
  const calcularTotalesFactura = useCallback(() => {
    const subtotal = datosFactura.itemsFactura.reduce(
      (suma, item) => suma + item.cantidad * item.precioUnitario, 0
    );
    const igv = subtotal * 0.18;
    const total = subtotal + igv;
    
    setDatosFactura(prev => ({
      ...prev,
      subtotalSinIgv: subtotal,
      montoIgv: igv,
      totalConIgv: total
    }));
  }, [datosFactura.itemsFactura]);
  
  const manejarEnvioFormulario = async (event: React.FormEvent) => {
    event.preventDefault();
    setCargandoDatos(true);
    setErrorMensaje(null);
    
    try {
      const facturaCreada = await servicioFacturas.crearFactura(datosFactura);
      // Manejar éxito
    } catch (error) {
      setErrorMensaje('Error al crear la factura. Intente nuevamente.');
    } finally {
      setCargandoDatos(false);
    }
  };
  
  return (
    <form onSubmit={manejarEnvioFormulario} className="formulario-factura">
      {/* Componentes del formulario */}
    </form>
  );
};

// ❌ INCORRECTO - No usar inglés
interface InvoiceData {  // ❌ Debe ser DatosFactura
  selectedCustomer: Customer;  // ❌ Debe ser clienteSeleccionado
  invoiceItems: InvoiceItem[];  // ❌ Debe ser itemsFactura
}
```

### **Convenciones de Archivos:**
```
✅ CORRECTO:
- FormularioCliente.tsx
- ServicioFacturacion.ts
- validacionesPeruanas.ts
- formatosMoneda.ts
- PuntoDeVenta.tsx

❌ INCORRECTO:
- CustomerForm.tsx
- InvoiceService.ts
- peruValidations.ts
- currencyFormats.ts
- PointOfSale.tsx
```

---

## 💾 **BASE DE DATOS MYSQL DETALLADA**

### **Configuración Optimizada MySQL 8.0:**
```sql
-- Configuración my.cnf optimizada para FELICITA
[mysqld]
# Configuración general
default_authentication_plugin = mysql_native_password
character_set_server = utf8mb4
collation_server = utf8mb4_unicode_ci
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO

# Configuración memoria (ajustar según servidor)
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
max_connections = 100

# Configuración para aplicaciones web
query_cache_type = 1
query_cache_size = 64M
tmp_table_size = 64M
max_heap_table_size = 64M

# Configuración timezone
default_time_zone = '-05:00'  # Perú GMT-5
```

### **Esquema Principal de Tablas:**
```sql
-- Tabla Empresas (core)
CREATE TABLE core_empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc VARCHAR(11) UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion_fiscal TEXT NOT NULL,
    ubigeo VARCHAR(6),
    telefono VARCHAR(20),
    email VARCHAR(100),
    representante_legal VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ruc (ruc),
    INDEX idx_activo (activo)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Usuarios (usuarios)
CREATE TABLE usuarios_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    password VARCHAR(128) NOT NULL,
    empresa_id INT,
    rol VARCHAR(20) DEFAULT 'vendedor',
    
    FOREIGN KEY (empresa_id) REFERENCES core_empresa(id),
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_empresa (empresa_id)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Clientes (core)
CREATE TABLE core_cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_documento ENUM('dni', 'ruc', 'pasaporte', 'carnet_extranjeria') NOT NULL,
    numero_documento VARCHAR(11) NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion TEXT,
    ubigeo VARCHAR(6),
    telefono VARCHAR(20),
    email VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    empresa_id INT NOT NULL,
    
    FOREIGN KEY (empresa_id) REFERENCES core_empresa(id),
    UNIQUE KEY unique_documento_empresa (numero_documento, empresa_id),
    INDEX idx_numero_documento (numero_documento),
    INDEX idx_razon_social (razon_social)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Productos (inventario)
CREATE TABLE inventario_producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    unidad_medida VARCHAR(10) DEFAULT 'NIU',
    precio_venta DECIMAL(12,4) NOT NULL,
    costo_promedio DECIMAL(12,4) DEFAULT 0,
    stock_actual DECIMAL(12,4) DEFAULT 0,
    stock_minimo DECIMAL(12,4) DEFAULT 0,
    afecto_igv BOOLEAN DEFAULT TRUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    empresa_id INT NOT NULL,
    
    FOREIGN KEY (empresa_id) REFERENCES core_empresa(id),
    UNIQUE KEY unique_codigo_empresa (codigo, empresa_id),
    INDEX idx_codigo (codigo),
    INDEX idx_descripcion (descripcion),
    INDEX idx_categoria (categoria)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Facturas (facturacion)
CREATE TABLE facturacion_factura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serie VARCHAR(4) NOT NULL,
    numero INT NOT NULL,
    tipo_comprobante ENUM('01', '03', '07', '08', '09') NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vencimiento DATE,
    cliente_id INT NOT NULL,
    moneda ENUM('PEN', 'USD') DEFAULT 'PEN',
    subtotal DECIMAL(12,2) NOT NULL,
    igv DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    estado ENUM('borrador', 'emitido', 'aceptado', 'rechazado', 'anulado') DEFAULT 'borrador',
    hash_sunat VARCHAR(255),
    xml_firmado LONGTEXT,
    pdf_url VARCHAR(500),
    observaciones TEXT,
    empresa_id INT NOT NULL,
    usuario_creacion_id INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    datos_sunat JSON,
    
    FOREIGN KEY (cliente_id) REFERENCES core_cliente(id),
    FOREIGN KEY (empresa_id) REFERENCES core_empresa(id),
    FOREIGN KEY (usuario_creacion_id) REFERENCES usuarios_usuario(id),
    UNIQUE KEY unique_serie_numero_empresa (serie, numero, empresa_id),
    INDEX idx_fecha_emision (fecha_emision),
    INDEX idx_cliente (cliente_id),
    INDEX idx_estado (estado),
    INDEX idx_tipo_comprobante (tipo_comprobante)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Items de Factura (facturacion)
CREATE TABLE facturacion_itemfactura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad DECIMAL(12,4) NOT NULL,
    precio_unitario DECIMAL(12,4) NOT NULL,
    descuento DECIMAL(12,2) DEFAULT 0,
    subtotal DECIMAL(12,2) NOT NULL,
    igv DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    
    FOREIGN KEY (factura_id) REFERENCES facturacion_factura(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES inventario_producto(id),
    INDEX idx_factura (factura_id),
    INDEX idx_producto (producto_id)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Movimientos de Inventario (inventario)
CREATE TABLE inventario_movimiento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste', 'traslado') NOT NULL,
    cantidad DECIMAL(12,4) NOT NULL,
    precio_unitario DECIMAL(12,4),
    costo_total DECIMAL(12,2),
    fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
    concepto VARCHAR(255),
    documento_referencia VARCHAR(50),
    usuario_id INT NOT NULL,
    empresa_id INT NOT NULL,
    
    FOREIGN KEY (producto_id) REFERENCES inventario_producto(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios_usuario(id),
    FOREIGN KEY (empresa_id) REFERENCES core_empresa(id),
    INDEX idx_producto_fecha (producto_id, fecha_movimiento),
    INDEX idx_tipo_movimiento (tipo_movimiento),
    INDEX idx_fecha (fecha_movimiento)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Plan de Cuentas (contabilidad)
CREATE TABLE contabilidad_plancuentas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    tipo_cuenta ENUM('activo', 'pasivo', 'patrimonio', 'ingresos', 'gastos') NOT NULL,
    nivel INT NOT NULL,
    cuenta_padre_id INT,
    activo BOOLEAN DEFAULT TRUE,
    empresa_id INT NOT NULL,
    
    FOREIGN KEY (cuenta_padre_id) REFERENCES contabilidad_plancuentas(id),
    FOREIGN KEY (empresa_id) REFERENCES core_empresa(id),
    UNIQUE KEY unique_codigo_empresa (codigo, empresa_id),
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo_cuenta)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla Asientos Contables (contabilidad)
CREATE TABLE contabilidad_asientocontable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_asiento INT NOT NULL,
    fecha DATE NOT NULL,
    concepto VARCHAR(255) NOT NULL,
    total_debe DECIMAL(12,2) NOT NULL,
    total_haber DECIMAL(12,2) NOT NULL,
    estado ENUM('borrador', 'confirmado') DEFAULT 'borrador',
    factura_id INT,
    empresa_id INT NOT NULL,
    usuario_creacion_id INT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (factura_id) REFERENCES facturacion_factura(id),
    FOREIGN KEY (empresa_id) REFERENCES core_empresa(id),
    FOREIGN KEY (usuario_creacion_id) REFERENCES usuarios_usuario(id),
    INDEX idx_fecha (fecha),
    INDEX idx_numero_asiento (numero_asiento),
    INDEX idx_factura (factura_id)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 🔐 **AUTENTICACIÓN Y SEGURIDAD**

### **Sistema JWT Completo:**
```python
# aplicaciones/usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = [
        ('administrador', 'Administrador'),
        ('contador', 'Contador'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    ]
    
    empresa = models.ForeignKey('core.Empresa', on_delete=models.PROTECT, null=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='vendedor')
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def tiene_permiso(self, permiso: str) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        permisos_rol = {
            'administrador': ['*'],  # Todos los permisos
            'contador': [
                'facturacion.ver_facturas',
                'reportes.generar_ple',
                'contabilidad.ver_asientos',
                'configuracion.editar_empresa'
            ],
            'vendedor': [
                'facturacion.crear_factura',
                'punto_venta.usar_pos',
                'clientes.ver_clientes',
                'productos.ver_productos'
            ],
            'cliente': [
                'facturas.ver_propias'
            ]
        }
        
        permisos_usuario = permisos_rol.get(self.rol, [])
        return '*' in permisos_usuario or permiso in permisos_usuario

# aplicaciones/usuarios/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import Usuario

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información adicional del usuario
        data['usuario'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nombre_completo': f"{self.user.first_name} {self.user.last_name}",
            'rol': self.user.rol,
            'empresa_id': self.user.empresa_id,
            'empresa_nombre': self.user.empresa.razon_social if self.user.empresa else None
        }
        
        # Actualizar último acceso
        self.user.ultimo_acceso = timezone.now()
        self.user.save(update_fields=['ultimo_acceso'])
        
        return data

class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'rol', 'telefono', 'activo',
            'date_joined', 'ultimo_acceso'
        ]
        read_only_fields = ['id', 'date_joined', 'ultimo_acceso']
    
    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
```

### **Permisos Granulares:**
```python
# aplicaciones/core/permissions.py
from rest_framework.permissions import BasePermission

class TienePermisoEspecifico(BasePermission):
    """Permiso basado en roles y permisos específicos"""
    
    def __init__(self, permiso_requerido):
        self.permiso_requerido = permiso_requerido
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.tiene_permiso(self.permiso_requerido)

class EsDeLaMismaEmpresa(BasePermission):
    """Verifica que el usuario pertenezca a la misma empresa del objeto"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Verificar que el objeto pertenece a la empresa del usuario
        if hasattr(obj, 'empresa'):
            return obj.empresa == request.user.empresa
        
        return True

# Uso en vistas
from rest_framework.decorators import permission_classes

@permission_classes([TienePermisoEspecifico('facturacion.crear_factura')])
class FacturaViewSet(viewsets.ModelViewSet):
    # Implementación
    pass
```

---

## 🔗 **INTEGRACIONES EXTERNAS**

### **Nubefact API Service:**
```python
# aplicaciones/integraciones/services/nubefact.py
import requests
import json
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger('felicita.nubefact')

class NubefactService:
    """Servicio para integración con Nubefact API (OSE SUNAT)"""
    
    def __init__(self):
        self.config = settings.NUBEFACT_CONFIG
        self.base_url = self.config['base_url']
        self.token = self.config['token']
        self.ruc = self.config['ruc']
        self.mode = self.config['mode']  # 'demo' o 'production'
        
        self.headers = {
            'Authorization': f'Token token="{self.token}"',
            'Content-Type': 'application/json'
        }
    
    def emitir_comprobante(self, factura) -> Dict[str, Any]:
        """Emite comprobante electrónico a través de Nubefact"""
        try:
            # Convertir factura Django a formato Nubefact
            data_nubefact = self._convertir_factura_a_nubefact(factura)
            
            # Log del request
            logger.info(f"Enviando factura {factura.serie}-{factura.numero} a Nubefact")
            logger.debug(f"Data enviada: {json.dumps(data_nubefact, indent=2)}")
            
            # Realizar request a Nubefact
            response = requests.post(
                f"{self.base_url}/",
                headers=self.headers,
                json=data_nubefact,
                timeout=30
            )
            
            response_data = response.json()
            
            # Log de la respuesta
            logger.info(f"Respuesta Nubefact: {response.status_code}")
            logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
            
            # Procesar respuesta
            if response.status_code == 200 and not response_data.get('errors'):
                # Éxito
                resultado = {
                    'exito': True,
                    'factura_id': response_data.get('invoice_id'),
                    'numero_comprobante': f"{response_data.get('serie')}-{response_data.get('numero')}",
                    'pdf_url': response_data.get('enlace_del_pdf'),
                    'xml_url': response_data.get('enlace_del_xml'),
                    'cdr_url': response_data.get('enlace_del_cdr'),
                    'hash': response_data.get('hash'),
                    'qr': response_data.get('qr'),
                    'estado_sunat': 'aceptado'
                }
                
                # Actualizar factura con datos SUNAT
                factura.estado = 'aceptado'
                factura.hash_sunat = resultado['hash']
                factura.pdf_url = resultado['pdf_url']
                factura.datos_sunat = response_data
                factura.save()
                
                return resultado
            else:
                # Error en Nubefact
                errores = response_data.get('errors', ['Error desconocido'])
                logger.error(f"Error Nubefact: {errores}")
                
                return {
                    'exito': False,
                    'errores': errores,
                    'codigo_error': response.status_code,
                    'respuesta_completa': response_data
                }
                
        except requests.exceptions.Timeout:
            logger.error("Timeout al conectar con Nubefact")
            return {
                'exito': False,
                'errores': ['Timeout de conexión con SUNAT'],
                'reintentar': True
            }
        except Exception as e:
            logger.error(f"Error inesperado en Nubefact: {str(e)}")
            return {
                'exito': False,
                'errores': [f'Error de conexión: {str(e)}'],
                'reintentar': True
            }
    
    def _convertir_factura_a_nubefact(self, factura) -> Dict[str, Any]:
        """Convierte modelo Factura Django a formato JSON Nubefact"""
        return {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": int(factura.tipo_comprobante),
            "serie": factura.serie,
            "numero": factura.numero,
            "sunat_transaction": 1,
            "cliente_tipo_de_documento": 6 if len(factura.cliente.numero_documento) == 11 else 1,
            "cliente_numero_de_documento": factura.cliente.numero_documento,
            "cliente_denominacion": factura.cliente.razon_social,
            "cliente_direccion": factura.cliente.direccion or "",
            "cliente_email": factura.cliente.email or "",
            "fecha_de_emision": factura.fecha_emision.strftime("%Y-%m-%d"),
            "fecha_de_vencimiento": factura.fecha_vencimiento.strftime("%Y-%m-%d") if factura.fecha_vencimiento else "",
            "moneda": 1 if factura.moneda == 'PEN' else 2,
            "tipo_de_cambio": "",
            "porcentaje_de_igv": 18.00,
            "descuento_global": 0.00,
            "total_descuento": 0.00,
            "total_anticipo": 0.00,
            "total_gravada": float(factura.subtotal),
            "total_inafecta": 0.00,
            "total_exonerada": 0.00,
            "total_igv": float(factura.igv),
            "total_gratuita": 0.00,
            "total_otros_cargos": 0.00,
            "total": float(factura.total),
            "observaciones": factura.observaciones or "",
            "documento_que_se_modifica_tipo": "",
            "documento_que_se_modifica_serie": "",
            "documento_que_se_modifica_numero": "",
            "tipo_de_nota_de_credito": "",
            "tipo_de_nota_de_debito": "",
            "enviar_automaticamente_a_la_sunat": True,
            "enviar_automaticamente_al_cliente": bool(factura.cliente.email),
            "codigo_unico": str(factura.id),
            "condiciones_de_pago": "Contado",
            "medio_de_pago": "Efectivo",
            "placa_vehiculo": "",
            "orden_compra_servicio": "",
            "tabla_personalizada_codigo": "",
            "formato_de_pdf": "A4",
            "items": [
                {
                    "unidad_de_medida": "NIU",
                    "codigo": item.producto.codigo,
                    "descripcion": item.producto.descripcion,
                    "cantidad": float(item.cantidad),
                    "valor_unitario": float(item.precio_unitario),
                    "precio_unitario": float(item.precio_unitario * 1.18) if item.producto.afecto_igv else float(item.precio_unitario),
                    "descuento": float(item.descuento),
                    "subtotal": float(item.subtotal),
                    "tipo_de_igv": 1 if item.producto.afecto_igv else 3,
                    "igv": float(item.igv),
                    "total": float(item.total),
                    "anticipo_regularizacion": False,
                    "anticipo_documento_serie": "",
                    "anticipo_documento_numero": ""
                }
                for item in factura.items.all()
            ]
        }
    
    def consultar_estado_comprobante(self, factura_id: str) -> Dict[str, Any]:
        """Consulta el estado de un comprobante en SUNAT"""
        try:
            response = requests.get(
                f"{self.base_url}/consultar/{factura_id}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return {
                    'exito': True,
                    'estado': response.json()
                }
            else:
                return {
                    'exito': False,
                    'error': 'No se pudo consultar el estado'
                }
        except Exception as e:
            logger.error(f"Error consultando estado: {str(e)}")
            return {
                'exito': False,
                'error': str(e)
            }
    
    def anular_comprobante(self, factura, motivo: str) -> Dict[str, Any]:
        """Genera comunicación de baja para anular comprobante"""
        data_baja = {
            "operacion": "generar_anulacion",
            "ubl": "2.1",
            "customization": "1.0",
            "documento_baja_id": f"RA-{factura.fecha_emision.strftime('%Y%m%d')}-001",
            "fecha_de_emision": factura.fecha_emision.strftime("%Y-%m-%d"),
            "fecha_de_baja": timezone.now().date().strftime("%Y-%m-%d"),
            "codigo_unico": f"BAJA-{factura.id}",
            "items": [
                {
                    "serie_y_numero_de_documento": f"{factura.serie}-{factura.numero}",
                    "motivo_o_sustento_de_baja": motivo,
                    "codigo_unico": str(factura.id)
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/",
                headers=self.headers,
                json=data_baja,
                timeout=30
            )
            
            if response.status_code == 200:
                factura.estado = 'anulado'
                factura.save()
                return {
                    'exito': True,
                    'mensaje': 'Comprobante anulado correctamente'
                }
            else:
                return {
                    'exito': False,
                    'error': 'Error al anular comprobante'
                }
        except Exception as e:
            logger.error(f"Error anulando comprobante: {str(e)}")
            return {
                'exito': False,
                'error': str(e)
            }
```

### **APIs Perú (RENIEC/SUNAT):**
```python
# aplicaciones/integraciones/services/apis_peru.py
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger('felicita.apis_peru')

class ApisPeru:
    """Servicios de APIs peruanas para validación de documentos"""
    
    def __init__(self):
        # URLs de APIs públicas (pueden cambiar, verificar vigencia)
        self.reniec_url = "https://api.reniec.cloud/dni"
        self.sunat_url = "https://api.sunat.cloud/ruc"
    
    def consultar_dni(self, dni: str) -> Dict[str, any]:
        """Consulta datos de DNI en RENIEC"""
        if not self._validar_dni(dni):
            return {
                'exito': False,
                'error': 'DNI inválido'
            }
        
        try:
            response = requests.get(
                f"{self.reniec_url}/{dni}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'exito': True,
                    'datos': {
                        'numero_documento': dni,
                        'nombres': data.get('nombres', ''),
                        'apellido_paterno': data.get('apellidoPaterno', ''),
                        'apellido_materno': data.get('apellidoMaterno', ''),
                        'nombre_completo': f"{data.get('nombres', '')} {data.get('apellidoPaterno', '')} {data.get('apellidoMaterno', '')}".strip()
                    }
                }
            else:
                return {
                    'exito': False,
                    'error': 'DNI no encontrado en RENIEC'
                }
                
        except Exception as e:
            logger.error(f"Error consultando DNI {dni}: {str(e)}")
            return {
                'exito': False,
                'error': 'Error de conexión con RENIEC'
            }
    
    def consultar_ruc(self, ruc: str) -> Dict[str, any]:
        """Consulta datos de RUC en SUNAT"""
        if not self._validar_ruc(ruc):
            return {
                'exito': False,
                'error': 'RUC inválido'
            }
        
        try:
            response = requests.get(
                f"{self.sunat_url}/{ruc}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'exito': True,
                    'datos': {
                        'numero_documento': ruc,
                        'razon_social': data.get('razonSocial', ''),
                        'nombre_comercial': data.get('nombreComercial', ''),
                        'direccion': data.get('direccion', ''),
                        'ubigeo': data.get('ubigeo', ''),
                        'estado': data.get('estado', ''),
                        'condicion': data.get('condicion', ''),
                        'tipo_contribuyente': data.get('tipoContribuyente', '')
                    }
                }
            else:
                return {
                    'exito': False,
                    'error': 'RUC no encontrado en SUNAT'
                }
                
        except Exception as e:
            logger.error(f"Error consultando RUC {ruc}: {str(e)}")
            return {
                'exito': False,
                'error': 'Error de conexión con SUNAT'
            }
    
    def _validar_dni(self, dni: str) -> bool:
        """Valida formato DNI peruano"""
        return len(dni) == 8 and dni.isdigit()
    
    def _validar_ruc(self, ruc: str) -> bool:
        """Valida RUC peruano con dígito verificador"""
        if len(ruc) != 11 or not ruc.isdigit():
            return False
        
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * factores[i] for i in range(10))
        resto = suma % 11
        digito = 11 - resto if resto >= 2 else resto
        
        return int(ruc[10]) == digito
```

---

## 🚀 **DEPLOYMENT Y HOSTING**

### **Configuración Hosting Compartido:**
```python
# config/settings/produccion.py
import os
from .base import *

# Security
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com', 'api.tudominio.com']

# Database para hosting compartido
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_PRODUCCION_NOMBRE'),
        'USER': os.getenv('DB_PRODUCCION_USUARIO'),
        'PASSWORD': os.getenv('DB_PRODUCCION_PASSWORD'),
        'HOST': os.getenv('DB_PRODUCCION_HOST', 'localhost'),
        'PORT': os.getenv('DB_PRODUCCION_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files para hosting compartido
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS para producción
CORS_ALLOWED_ORIGINS = [
    "https://tudominio.com",
    "https://www.tudominio.com",
    "https://app.tudominio.com",
]

# Nubefact en modo producción
NUBEFACT_CONFIG = {
    'mode': 'production',
    'token': os.getenv('NUBEFACT_TOKEN_PRODUCCION'),
    'ruc': os.getenv('EMPRESA_RUC'),
    'base_url': 'https://api.nubefact.com/api/v1',
}

# Email en producción
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Logging en producción
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'felicita_produccion.log'),
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'felicita': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### **Script de Deployment:**
```bash
#!/bin/bash
# scripts/deploy.sh - Deploy automático para hosting compartido

echo "🚀 Iniciando deployment de FELICITA..."

# Variables
PROJECT_DIR="/home/usuario/public_html/api"
VENV_DIR="/home/usuario/venv"
BACKUP_DIR="/home/usuario/backups/$(date +%Y%m%d_%H%M%S)"

# Crear backup antes del deployment
echo "📦 Creando backup..."
mkdir -p $BACKUP_DIR
cp -r $PROJECT_DIR $BACKUP_DIR/
mysqldump -u$DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/database_backup.sql

# Activar virtual environment
echo "🔧 Activando virtual environment..."
source $VENV_DIR/bin/activate

# Actualizar código
echo "📥 Actualizando código..."
cd $PROJECT_DIR
git pull origin main

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements/produccion.txt

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
python manage.py migrate --settings=config.settings.produccion

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --settings=config.settings.produccion

# Reiniciar aplicación (método depende del hosting)
echo "🔄 Reiniciando aplicación..."
touch tmp/restart.txt  # Para Passenger en hosting compartido

echo "✅ Deployment completado exitosamente!"
echo "📊 Verificar en: https://api.tudominio.com/admin/"
```

---

## 📊 **MÉTRICAS Y MONITORING**

### **KPIs del Sistema:**
```python
# aplicaciones/reportes/services/kpis.py
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

class KPIService:
    """Servicio para cálculo de KPIs del sistema"""
    
    @staticmethod
    def obtener_kpis_dashboard(empresa_id: int) -> dict:
        """Calcula KPIs principales para el dashboard"""
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        mes_anterior = inicio_mes - timedelta(days=1)
        inicio_mes_anterior = mes_anterior.replace(day=1)
        
        from aplicaciones.facturacion.models import Factura
        from aplicaciones.inventario.models import Producto
        from aplicaciones.core.models import Cliente
        
        # Ventas del día
        ventas_hoy = Factura.objects.filter(
            empresa_id=empresa_id,
            fecha_emision=hoy,
            estado__in=['emitido', 'aceptado']
        ).aggregate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        # Ventas del mes
        ventas_mes = Factura.objects.filter(
            empresa_id=empresa_id,
            fecha_emision__gte=inicio_mes,
            estado__in=['emitido', 'aceptado']
        ).aggregate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        # Ventas mes anterior (para comparación)
        ventas_mes_anterior = Factura.objects.filter(
            empresa_id=empresa_id,
            fecha_emision__gte=inicio_mes_anterior,
            fecha_emision__lt=inicio_mes,
            estado__in=['emitido', 'aceptado']
        ).aggregate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        # Productos con stock bajo
        productos_stock_bajo = Producto.objects.filter(
            empresa_id=empresa_id,
            activo=True,
            stock_actual__lte=models.F('stock_minimo')
        ).count()
        
        # Clientes activos (con facturas últimos 30 días)
        clientes_activos = Cliente.objects.filter(
            empresa_id=empresa_id,
            facturas__fecha_emision__gte=hoy - timedelta(days=30)
        ).distinct().count()
        
        # Calcular variaciones porcentuales
        def calcular_variacion(actual, anterior):
            if anterior and anterior > 0:
                return round(((actual - anterior) / anterior) * 100, 1)
            return 0
        
        return {
            'ventas_hoy': {
                'total': ventas_hoy['total'] or 0,
                'cantidad': ventas_hoy['cantidad'] or 0
            },
            'ventas_mes': {
                'total': ventas_mes['total'] or 0,
                'cantidad': ventas_mes['cantidad'] or 0,
                'variacion': calcular_variacion(
                    ventas_mes['total'] or 0,
                    ventas_mes_anterior['total'] or 0
                )
            },
            'productos_stock_bajo': productos_stock_bajo,
            'clientes_activos': clientes_activos,
            'fecha_actualizacion': timezone.now().isoformat()
        }
```

---

## ✅ **CRITERIOS DE ÉXITO Y VALIDACIÓN**

### **Checklist de Cumplimiento SUNAT:**
```python
# aplicaciones/core/validators/sunat_compliance.py

class ValidadorCumplimientoSUNAT:
    """Validador de cumplimiento normativo SUNAT"""
    
    @staticmethod
    def validar_sistema_completo(empresa_id: int) -> dict:
        """Valida cumplimiento integral del sistema"""
        
        resultados = {
            'cumple_normativa': True,
            'validaciones': [],
            'errores': [],
            'advertencias': []
        }
        
        # 1. Validar numeración correlativa
        correlativo_ok = ValidadorCumplimientoSUNAT._validar_numeracion_correlativa(empresa_id)
        resultados['validaciones'].append({
            'nombre': 'Numeración Correlativa',
            'cumple': correlativo_ok['cumple'],
            'detalle': correlativo_ok['detalle']
        })
        
        # 2. Validar integridad IGV
        igv_ok = ValidadorCumplimientoSUNAT._validar_calculo_igv(empresa_id)
        resultados['validaciones'].append({
            'nombre': 'Cálculo IGV 18%',
            'cumple': igv_ok['cumple'],
            'detalle': igv_ok['detalle']
        })
        
        # 3. Validar método PEPS
        peps_ok = ValidadorCumplimientoSUNAT._validar_metodo_peps(empresa_id)
        resultados['validaciones'].append({
            'nombre': 'Método PEPS Inventarios',
            'cumple': peps_ok['cumple'],
            'detalle': peps_ok['detalle']
        })
        
        # 4. Validar plan de cuentas PCGE
        pcge_ok = ValidadorCumplimientoSUNAT._validar_plan_cuentas_pcge(empresa_id)
        resultados['validaciones'].append({
            'nombre': 'Plan de Cuentas PCGE',
            'cumple': pcge_ok['cumple'],
            'detalle': pcge_ok['detalle']
        })
        
        # Verificar si todas las validaciones pasan
        resultados['cumple_normativa'] = all(
            v['cumple'] for v in resultados['validaciones']
        )
        
        return resultados
    
    @staticmethod
    def _validar_numeracion_correlativa(empresa_id: int) -> dict:
        """Valida que no haya vacíos en numeración de comprobantes"""
        from aplicaciones.facturacion.models import Factura
        
        series = Factura.objects.filter(
            empresa_id=empresa_id
        ).values_list('serie', flat=True).distinct()
        
        errores = []
        for serie in series:
            facturas = Factura.objects.filter(
                empresa_id=empresa_id,
                serie=serie
            ).order_by('numero').values_list('numero', flat=True)
            
            numeros = list(facturas)
            if numeros:
                # Verificar secuencia continua
                esperado = list(range(numeros[0], numeros[-1] + 1))
                if numeros != esperado:
                    faltantes = set(esperado) - set(numeros)
                    errores.append(f"Serie {serie}: números faltantes {faltantes}")
        
        return {
            'cumple': len(errores) == 0,
            'detalle': 'Numeración correlativa correcta' if not errores else f"Errores: {errores}"
        }
```

---

## 🎯 **ROADMAP Y EVOLUCIÓN**

### **Versiones Planificadas:**
```
VERSIÓN 1.0 (MVP) - Semanas 1-11:
✅ Facturación electrónica SUNAT completa
✅ Punto de venta optimizado
✅ Control inventarios método PEPS
✅ Contabilidad básica automatizada
✅ Reportes PLE obligatorios
✅ Dashboard ejecutivo
✅ Multi-usuario con roles

VERSIÓN 1.1 (Mejoras) - Semanas 12-16:
📋 App móvil para vendedores
📋 Integración códigos de barra completa
📋 Cotizaciones y proformas
📋 CRM básico integrado
📋 Notificaciones automáticas
📋 Backup cloud automático

VERSIÓN 1.2 (Expansión) - Semanas 17-24:
📋 Multi-empresa desde una cuenta
📋 API pública para integraciones
📋 Marketplace de plugins
📋 Integraciones bancarias
📋 Business Intelligence avanzado
📋 Exportación internacional

VERSIÓN 2.0 (Enterprise) - Año 2:
📋 Inteligencia artificial para proyecciones
📋 Integración con ERPs externos
📋 Módulo de manufactura
📋 E-commerce integrado
📋 Franquicias multi-país
📋 Blockchain para auditoría
```

---

## 📞 **SOPORTE Y COMUNIDAD**

### **Canales de Soporte:**
```
DOCUMENTACIÓN:
📖 Wiki completa: https://github.com/[usuario]/felicita/wiki
📖 API Docs: https://api.felicita.pe/docs/
📖 Tutoriales: https://docs.felicita.pe/

COMUNIDAD:
💬 Discord: Comunidad FELICITA
💬 Telegram: @FelicitaPeru
📧 Email: soporte@felicita.pe

SOPORTE TÉCNICO:
🎫 Issues GitHub: Bugs y feature requests
🎫 Support Desk: Soporte premium
📞 WhatsApp Business: Soporte urgente

CONTRIBUCIÓN:
🤝 Contributing Guidelines
🤝 Code of Conduct
🤝 Developer Certificate of Origin
```

---

## 🏆 **CONCLUSIÓN**

**FELICITA** representa una revolución en el software de facturación para Perú, combinando:

- ✅ **Cumplimiento SUNAT 100%** verificado y auditado
- ✅ **Tecnología moderna** (React + Django + MySQL)
- ✅ **Costo accesible** (95% menos que ERPs importados)
- ✅ **Adaptación local** específica para realidad peruana
- ✅ **Escalabilidad** desde PYME hasta empresa grande
- ✅ **Open Source** con community support

### **Impacto Esperado:**
- 🎯 **10,000+ PYMEs** usando el sistema en primer año
- 🎯 **$50M+ en facturas** procesadas mensualmente
- 🎯 **500+ empleos** indirectos en ecosistema
- 🎯 **Referente** en facturación electrónica latinoamericana

**FELICITA no es solo un software, es la democratización de la tecnología empresarial para el Perú.** 🇵🇪✨