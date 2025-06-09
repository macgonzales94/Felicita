# 🚀 FELICITA - Sistema de Facturación Electrónica para Perú

![FELICITA Logo](docs/images/logo-felicita.png)

**FELICITA** es un sistema completo de facturación electrónica diseñado específicamente para cumplir con la normativa SUNAT de Perú. Incluye facturación electrónica, punto de venta, control de inventarios, contabilidad y reportes avanzados.

## 📋 Tabla de Contenidos

- [🌟 Características](#-características)
- [🏗️ Arquitectura Técnica](#️-arquitectura-técnica)
- [📋 Requisitos](#-requisitos)
- [🚀 Instalación Rápida](#-instalación-rápida)
- [⚙️ Configuración Detallada](#️-configuración-detallada)
- [🔧 Desarrollo](#-desarrollo)
- [📚 Documentación](#-documentación)
- [🧪 Testing](#-testing)
- [🚢 Deployment](#-deployment)
- [🤝 Contribución](#-contribución)
- [📄 Licencia](#-licencia)

## 🌟 Características

### 📊 Módulos Principales

- **💰 Facturación Electrónica**
  - Facturas y boletas según normativa SUNAT
  - Notas de crédito y débito
  - Guías de remisión electrónicas
  - Integración con OSE (Nubefact)
  - Generación de XML UBL 2.1
  - Códigos QR automáticos

- **🛒 Punto de Venta (POS)**
  - Interfaz táctil optimizada
  - Múltiples métodos de pago
  - Gestión de cajas y turnos
  - Impresión automática de tickets
  - Lectura de códigos de barras

- **📦 Control de Inventarios**
  - Método PEPS (obligatorio SUNAT)
  - Múltiples almacenes
  - Control de lotes y vencimientos
  - Transferencias entre almacenes
  - Kardex automatizado
  - Alertas de stock bajo

- **📋 Contabilidad**
  - Plan Contable General Empresarial (PCGE)
  - Asientos contables automáticos
  - Libros electrónicos PLE
  - Estados financieros
  - Centros de costo

- **📈 Reportes y Analytics**
  - Dashboard ejecutivo
  - Reportes personalizables
  - KPIs en tiempo real
  - Exportación a Excel/PDF
  - Alertas automáticas

- **⚙️ Gestión Administrativa**
  - Gestión de usuarios y permisos
  - Configuración empresarial
  - Backup automático
  - Auditoría de acciones

### 🇵🇪 Cumplimiento Normativo Perú

- ✅ Facturación electrónica SUNAT
- ✅ Libros electrónicos PLE
- ✅ Método PEPS para inventarios
- ✅ IGV 18% automático
- ✅ Validación RUC/DNI
- ✅ Numeración correlativa
- ✅ Formato XML UBL 2.1

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

```mermaid
graph TB
    A[Frontend - React + TypeScript] --> B[API - Django REST Framework]
    B --> C[Base de Datos - PostgreSQL]
    B --> D[Cache - Redis]
    B --> E[OSE - Nubefact API]
    B --> F[APIs Perú - SUNAT/RENIEC]
    
    subgraph "Servicios Externos"
        E
        F
    end
    
    subgraph "Infraestructura"
        C
        D
    end
```

### Componentes Principales

- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Base de Datos:** PostgreSQL 15
- **Cache:** Redis 7
- **OSE:** Nubefact API
- **Containerización:** Docker + Docker Compose
- **Deployment:** DigitalOcean + Vercel

## 📋 Requisitos

### Software Requerido

- **Docker:** 20.10+ y Docker Compose v2
- **Python:** 3.8+ (para desarrollo backend)
- **Node.js:** 16+ y npm 7+ (para desarrollo frontend)
- **Git:** Para control de versiones

### Sistemas Operativos Soportados

- ✅ Linux (Ubuntu 20.04+, CentOS 8+)
- ✅ macOS (10.15+)
- ✅ Windows 10+ con WSL2

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/felicita.git
cd felicita
```

### 2. Ejecutar Script de Instalación

**En Linux/macOS:**
```bash
chmod +x iniciar-desarrollo.sh
./iniciar-desarrollo.sh
```

**En Windows:**
```cmd
iniciar-desarrollo.bat
```

### 3. Acceder al Sistema

Después de la instalación exitosa:

- 🌐 **Frontend:** http://localhost:3000
- 🔧 **API Backend:** http://localhost:8000
- 📋 **Admin Django:** http://localhost:8000/admin
- 🗄️ **Adminer (DB):** http://localhost:8080

**Credenciales por defecto:**
- Email: `admin@felicita.pe`
- Password: `admin123`

## ⚙️ Configuración Detallada

### Variables de Entorno

Copia y configura los archivos de entorno:

```bash
# Backend
cp .env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

### Configuración de Base de Datos

El sistema usa PostgreSQL con las siguientes configuraciones por defecto:

```env
DB_NAME=felicita_db
DB_USER=felicita_user
DB_PASSWORD=felicita_2024_dev
DB_HOST=localhost
DB_PORT=5432
```

### Configuración de Nubefact

Para integración con SUNAT a través de Nubefact:

```env
NUBEFACT_MODO=demo  # o 'produccion'
NUBEFACT_TOKEN=tu_token_nubefact
NUBEFACT_RUC_EMISOR=20123456789
```

## 🔧 Desarrollo

### Estructura del Proyecto

```
felicita/
├── backend/                 # Django API
│   ├── felicita/           # Configuración principal
│   ├── aplicaciones/       # Apps Django
│   │   ├── core/          # Modelos base
│   │   ├── usuarios/      # Autenticación
│   │   ├── facturacion/   # Facturación electrónica
│   │   ├── inventario/    # Control de inventarios
│   │   ├── contabilidad/  # Contabilidad
│   │   ├── punto_venta/   # POS
│   │   ├── reportes/      # Reportes y analytics
│   │   └── integraciones/ # APIs externas
│   ├── fixtures/          # Datos iniciales
│   └── requirements.txt
├── frontend/               # React TypeScript
│   ├── src/
│   │   ├── componentes/   # Componentes React
│   │   ├── paginas/       # Páginas principales
│   │   ├── servicios/     # API calls
│   │   ├── hooks/         # Custom hooks
│   │   ├── contextos/     # React Context
│   │   ├── utils/         # Utilidades
│   │   └── types/         # TypeScript types
│   └── package.json
├── docker-compose.yml      # Servicios Docker
└── README.md
```

### Comandos de Desarrollo

#### Backend (Django)

```bash
cd backend

# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate.bat  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Cargar datos iniciales
python manage.py loaddata fixtures/datos_iniciales.json

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```

#### Frontend (React)

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Ejecutar tests
npm test

# Linting y formato
npm run lint
npm run format
```

#### Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Limpiar todo
docker-compose down -v --rmi all
```

### API Endpoints Principales

#### Autenticación
```
POST /api/auth/login/          # Iniciar sesión
POST /api/auth/logout/         # Cerrar sesión
POST /api/auth/refresh/        # Refrescar token
GET  /api/auth/profile/        # Perfil de usuario
```

#### Core
```
GET  /api/core/empresas/       # Listar empresas
GET  /api/core/clientes/       # Listar clientes
GET  /api/core/productos/      # Listar productos
```

#### Facturación
```
GET  /api/facturacion/facturas/     # Listar facturas
POST /api/facturacion/facturas/     # Crear factura
GET  /api/facturacion/facturas/{id}/# Obtener factura
```

## 📚 Documentación

### Documentación API

- **Swagger UI:** http://localhost:8000/docs/
- **ReDoc:** http://localhost:8000/redoc/
- **JSON Schema:** http://localhost:8000/api/schema/

### Documentación Adicional

- [📖 Guía de Usuario](docs/MANUAL_USUARIO.md)
- [🏗️ Arquitectura del Sistema](docs/ARQUITECTURA.md)
- [🚀 Guía de Deployment](docs/DEPLOYMENT.md)
- [🔧 Troubleshooting](docs/TROUBLESHOOTING.md)

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Ejecutar todos los tests
python manage.py test

# Tests con coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Tests

```bash
cd frontend

# Ejecutar tests
npm test

# Tests con coverage
npm run test:coverage

# Tests en modo watch
npm run test:watch
```

### Tests de Integración

```bash
# Tests end-to-end con Playwright
npm run test:e2e
```

## 🚢 Deployment

### Desarrollo

El sistema está configurado para ejecutarse completamente en local usando Docker:

```bash
./iniciar-desarrollo.sh
```

### Producción

#### Backend (DigitalOcean App Platform)

1. Crear app en DigitalOcean
2. Conectar repositorio
3. Configurar variables de entorno
4. Deploy automático desde main branch

#### Frontend (Vercel)

1. Conectar repositorio a Vercel
2. Configurar build settings:
   ```
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```
3. Configurar variables de entorno
4. Deploy automático

### Variables de Entorno Producción

```env
# Django
DEBUG=False
SECRET_KEY=tu_secret_key_produccion
ALLOWED_HOSTS=api.tudominio.com

# Base de datos
DATABASE_URL=postgresql://user:pass@host:port/db

# Nubefact
NUBEFACT_MODO=produccion
NUBEFACT_TOKEN=tu_token_produccion

# CORS
CORS_ALLOWED_ORIGINS=https://app.tudominio.com
```

## 🤝 Contribución

### Flujo de Desarrollo

1. Fork del repositorio
2. Crear branch para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código

#### Python (Backend)
- Seguir PEP 8
- Usar black para formateo
- Usar flake8 para linting
- Cobertura de tests > 80%

#### TypeScript (Frontend)
- Seguir estándares de ESLint
- Usar Prettier para formateo
- Componentes funcionales con hooks
- Props tipadas con TypeScript

### Nomenclatura

**IMPORTANTE:** Todo el código debe estar en español:

```python
# ✅ Correcto
class Cliente(models.Model):
    razon_social = models.CharField()
    numero_documento = models.CharField()

# ❌ Incorrecto
class Customer(models.Model):
    company_name = models.CharField()
    document_number = models.CharField()
```

```typescript
// ✅ Correcto
interface DatosFactura {
  clienteSeleccionado: Cliente;
  totalConIgv: number;
}

// ❌ Incorrecto
interface InvoiceData {
  selectedCustomer: Customer;
  totalWithTax: number;
}
```

## 📊 Roadmap

### Versión 1.0 (Actual)
- ✅ Facturación electrónica básica
- ✅ Punto de venta
- ✅ Control de inventarios
- ✅ Contabilidad básica

### Versión 1.1 (Q2 2024)
- 🔄 Facturación masiva
- 🔄 Reportes avanzados
- 🔄 API pública
- 🔄 App móvil

### Versión 2.0 (Q4 2024)
- 📋 Integración con bancos
- 📋 Comercio electrónico
- 📋 Inteligencia artificial
- 📋 Multi-empresa

## 🐛 Reporte de Bugs

Para reportar bugs, usar los [GitHub Issues](https://github.com/tu-usuario/felicita/issues) con la siguiente información:

- Versión del sistema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots si aplica
- Logs del error

## 💬 Soporte

- 📧 Email: soporte@felicita.pe
- 💬 Discord: [FELICITA Community](https://discord.gg/felicita)
- 📚 Wiki: [GitHub Wiki](https://github.com/tu-usuario/felicita/wiki)
- 🎥 Tutoriales: [YouTube Channel](https://youtube.com/felicita)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [Django](https://djangoproject.com/) - Framework web backend
- [React](https://reactjs.org/) - Librería frontend
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS
- [Nubefact](https://nubefact.com/) - OSE para facturación electrónica
- [SUNAT](https://sunat.gob.pe/) - Especificaciones técnicas

---

<div align="center">

**🚀 Desarrollado con ❤️ para empresas peruanas**

[Website](https://felicita.pe) • [Demo](https://demo.felicita.pe) • [Docs](https://docs.felicita.pe)

</div>