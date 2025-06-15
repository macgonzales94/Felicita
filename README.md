# 🇵🇪 FELICITA - Sistema de Facturación Electrónica para Perú

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![SUNAT](https://img.shields.io/badge/SUNAT-Compliant-green.svg)](https://sunat.gob.pe)

**FELICITA** es un sistema completo de facturación electrónica diseñado específicamente para el mercado peruano, que cumple al 100% con la normativa SUNAT y ofrece todas las funcionalidades necesarias para la gestión empresarial moderna.

---

## 🎯 **Características Principales**

### ✅ **Cumplimiento SUNAT 100%**
- Facturación electrónica según normativa UBL 2.1
- Integración con OSE certificado (Nubefact)
- Numeración correlativa automática
- Libros electrónicos PLE
- Validación de RUC y DNI peruanos

### 🏪 **Punto de Venta Moderno**
- Interfaz táctil optimizada para tablets
- Códigos de barra integrados
- Múltiples métodos de pago
- Cálculo automático de IGV (18%)
- Emisión inmediata de comprobantes

### 📦 **Control de Inventarios PEPS**
- Método PEPS obligatorio SUNAT
- Múltiples almacenes
- Alertas de stock mínimo/máximo
- Kardex automatizado
- Control de lotes y vencimientos

### 📊 **Contabilidad Automatizada**
- Plan de cuentas PCGE completo
- Asientos contables automáticos
- Estados financieros básicos
- Cuentas por cobrar/pagar
- Centro de costos

### 📈 **Reportes y Analytics**
- Dashboard ejecutivo con KPIs
- Reportes PLE formato SUNAT
- Análisis de ventas con gráficos
- Exportación Excel/PDF
- Business Intelligence básico

---

## 🏗️ **Arquitectura Técnica**

### **Stack Tecnológico**
```
Backend:    Django 4.2 + Django REST Framework + MySQL 8.0
Frontend:   React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
Cache:      Redis 7
Database:   MySQL 8.0 con AUTO_INCREMENT para numeración SUNAT
APIs:       Nubefact (OSE), RENIEC, SUNAT
Deploy:     Backend hosting compartido, Frontend Vercel
```

### **Estructura del Proyecto**
```
felicita/
├── backend/                 # Django Backend
│   ├── aplicaciones/        # Apps Django (core, usuarios, facturacion, etc.)
│   ├── config/             # Configuraciones Django
│   ├── fixtures/           # Datos iniciales
│   └── requirements.txt    # Dependencias Python
├── frontend/               # React Frontend
│   ├── src/               # Código fuente React
│   │   ├── componentes/   # Componentes reutilizables
│   │   ├── paginas/       # Páginas principales
│   │   ├── servicios/     # APIs y servicios
│   │   └── types/         # Interfaces TypeScript
│   └── package.json       # Dependencias Node.js
├── docker-compose.yml      # MySQL + phpMyAdmin + Redis
└── documentacion/          # Documentación completa
```

---

## 🚀 **Inicio Rápido**

### **Prerrequisitos**
- Python 3.9+ 
- Node.js 18+
- Docker y Docker Compose
- Git

### **Instalación Automática**

#### Linux/Mac:
```bash
git clone https://github.com/macgonzales94/felicita.git
cd felicita
chmod +x iniciar-desarrollo.sh
./iniciar-desarrollo.sh
```

#### Windows:
```cmd
git clone https://github.com/macgonzales94/felicita.git
cd felicita
iniciar-desarrollo.bat
```

### **Instalación Manual**

1. **Clonar el repositorio**
```bash
git clone https://github.com/macgonzales94/felicita.git
cd felicita
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Iniciar base de datos**
```bash
docker-compose up -d db redis phpmyadmin
```

4. **Configurar Backend Django**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. **Configurar Frontend React**
```bash
cd frontend
npm install
npm run dev
```

### **URLs de Desarrollo**
- 🌐 **Frontend React:** http://localhost:3000
- 🔧 **Backend Django:** http://localhost:8000
- 📊 **Admin Django:** http://localhost:8000/admin/
- 🗄️ **phpMyAdmin:** http://localhost:8080
- 📱 **API Docs:** http://localhost:8000/api/docs/

### **Credenciales por Defecto**
- **Admin Django:** `admin` / `admin123`
- **MySQL Root:** `root` / `root_password_123`
- **MySQL Usuario:** `felicita_user` / `dev_password_123`

---

## 📋 **Módulos del Sistema**

### 🏢 **Core (Entidades Base)**
- Gestión de empresas y sucursales
- Configuración del sistema
- Catálogos SUNAT

### 👥 **Usuarios**
- Autenticación JWT
- Roles: Administrador, Contador, Vendedor, Cliente
- Permisos granulares

### 🧾 **Facturación Electrónica**
- Facturas, boletas, notas de crédito/débito
- Integración Nubefact (OSE certificado)
- Validación XML UBL 2.1
- Numeración correlativa automática

### 🛒 **Punto de Venta**
- Interfaz táctil moderna
- Búsqueda rápida de productos
- Múltiples métodos de pago
- Impresión directa

### 📦 **Inventario**
- Método PEPS obligatorio
- Múltiples almacenes
- Kardex automatizado
- Alertas de stock

### 📚 **Contabilidad**
- Plan de cuentas PCGE
- Asientos automáticos
- Estados financieros
- Reportes contables

### 🔗 **Integraciones**
- Nubefact API (SUNAT OSE)
- RENIEC (validación DNI)
- SUNAT (validación RUC)
- Webhooks automáticos

### 📊 **Reportes**
- Dashboard ejecutivo
- Reportes PLE SUNAT
- Analytics de ventas
- Exportación múltiples formatos

---

## 🇵🇪 **Cumplimiento Normativo SUNAT**

### **Validaciones Implementadas**
- ✅ Numeración correlativa sin vacíos
- ✅ Cálculo IGV 18% automático
- ✅ Formato XML UBL 2.1 exacto
- ✅ Método PEPS para inventarios
- ✅ Plan de cuentas PCGE
- ✅ Libros electrónicos PLE
- ✅ Validación algoritmos RUC/DNI

### **Tipos de Comprobante Soportados**
- **01:** Factura
- **03:** Boleta de Venta
- **07:** Nota de Crédito
- **08:** Nota de Débito
- **09:** Guía de Remisión

### **Reportes PLE Automáticos**
- Registro de Ventas
- Registro de Compras
- Libro Diario
- Libro Mayor
- Inventarios Permanentes

---

## 🛠️ **Desarrollo y Contribución**

### **Estándares de Código**
- **Nomenclatura:** Español obligatorio
- **Backend:** PEP 8 para Python
- **Frontend:** ESLint + Prettier
- **Base de Datos:** Nomenclatura descriptiva
- **Git:** Conventional Commits

### **Tecnologías y Decisiones**
- **MySQL 8.0:** AUTO_INCREMENT para numeración SUNAT
- **React + TypeScript:** Tipado fuerte y componentes reutilizables
- **Tailwind CSS:** Diseño moderno y responsive
- **Django REST Framework:** API robusta y documentada

### **Contribuir al Proyecto**
1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📦 **Deployment**

### **Hosting Compartido (Recomendado)**
- Backend: Hosting compartido con MySQL ($3-10/mes)
- Frontend: Vercel/Netlify (gratis)
- Total: ~$5-15/mes vs $200+/mes ERPs tradicionales

### **Configuración Producción**
```bash
# Backend
cd backend
pip install -r requirements/produccion.txt
python manage.py collectstatic
python manage.py migrate --settings=config.settings.produccion

# Frontend
cd frontend
npm run build
# Deploy dist/ folder to Vercel/Netlify
```

---

## 📚 **Documentación**

- 📖 **[Guía de Instalación](documentacion/INSTALACION.md)**
- 🏗️ **[Arquitectura del Sistema](documentacion/ARQUITECTURA.md)**
- 📱 **[Documentación API](documentacion/API.md)**
- 🚀 **[Guía de Deployment](documentacion/DEPLOYMENT.md)**
- 👥 **[Manual de Usuario](documentacion/MANUAL_USUARIO.md)**
- 🧪 **[Guía de Testing](documentacion/TESTING.md)**

---

## 📞 **Soporte y Comunidad**

### **Canales de Soporte**
- 📧 **Email:** soporte@felicita.pe
- 💬 **Discord:** [Comunidad FELICITA](https://discord.gg/felicita)
- 📱 **Telegram:** [@FelicitaPeru](https://t.me/FelicitaPeru)
- 🎫 **Issues:** [GitHub Issues](https://github.com/macgonzales94/felicita/issues)

### **Recursos Adicionales**
- 📖 **Wiki:** [GitHub Wiki](https://github.com/macgonzales94/felicita/wiki)
- 📊 **API Docs:** [Swagger UI](http://localhost:8000/api/docs/)
- 🎥 **Tutoriales:** [YouTube Channel](https://youtube.com/@felicita-peru)

---

## 📄 **Licencia**

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

**Nota:** El uso comercial está permitido, pero se requiere mantener la atribución al proyecto original.

---

## 🙏 **Agradecimientos**

- **SUNAT** por las especificaciones técnicas de facturación electrónica
- **Nubefact** por proporcionar servicios OSE certificados
- **Comunidad Django** y **React** por las herramientas excepcionales
- **Desarrolladores peruanos** que contribuyen al ecosistema tech local

---

## 🎯 **Roadmap**

### **Versión 1.0 (Actual) - MVP**
- ✅ Facturación electrónica completa
- ✅ Punto de venta optimizado
- ✅ Control inventarios PEPS
- ✅ Contabilidad básica
- ✅ Reportes PLE

### **Versión 1.1 (Q2 2025)**
- 📱 App móvil para vendedores
- 🔍 Códigos de barra avanzados
- 📋 Cotizaciones y proformas
- 📧 Notificaciones automáticas

### **Versión 1.2 (Q3 2025)**
- 🏢 Multi-empresa
- 🔌 API pública
- 🏪 Marketplace de plugins
- 🏦 Integraciones bancarias

### **Versión 2.0 (2026)**
- 🤖 Inteligencia artificial
- 🌐 E-commerce integrado
- 🏭 Módulo manufactura
- 🔗 Blockchain audit trail

---

## 📊 **Estadísticas del Proyecto**

![GitHub stars](https://img.shields.io/github/stars/macgonzales94/felicita?style=social)
![GitHub forks](https://img.shields.io/github/forks/macgonzales94/felicita?style=social)
![GitHub issues](https://img.shields.io/github/issues/macgonzales94/felicita)
![GitHub pull requests](https://img.shields.io/github/issues-pr/macgonzales94/felicita)

---

<div align="center">

**¡FELICITA es más que un software, es la democratización de la tecnología empresarial para el Perú! 🇵🇪**

[⭐ Star](https://github.com/macgonzales94/felicita) | [🐛 Report Bug](https://github.com/macgonzales94/felicita/issues) | [💡 Request Feature](https://github.com/macgonzales94/felicita/issues)

**Hecho con ❤️ en Perú**

</div>