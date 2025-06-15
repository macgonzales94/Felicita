# INSTALACIÓN Y CONFIGURACIÓN FELICITA

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.9+
- Node.js 18+
- Docker y Docker Compose
- Git

### Instalación Automática

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

### URLs de Desarrollo
- 🌐 **Frontend React:** http://localhost:3000
- 🔧 **Backend Django:** http://localhost:8000
- 📊 **Admin Django:** http://localhost:8000/admin/
- 🗄️ **phpMyAdmin:** http://localhost:8080
- 📱 **API Docs:** http://localhost:8000/api/docs/

### Credenciales por Defecto
- **Admin:** admin / admin123
- **Contador:** contador / admin123
- **Vendedor:** vendedor / admin123

## 📁 Estructura del Proyecto

```
felicita/
├── backend/                 # Django Backend
│   ├── aplicaciones/        # Apps Django
│   │   ├── core/           # Entidades base
│   │   └── usuarios/       # Autenticación JWT
│   ├── config/             # Configuraciones
│   └── fixtures/           # Datos iniciales
├── frontend/               # React Frontend
│   └── src/               # Código React/TypeScript
├── docker-compose.yml      # MySQL + Redis + phpMyAdmin
└── documentacion/          # Documentación completa
```

## 🔧 Configuración Manual

### 1. Backend Django
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/datos_iniciales.json
python manage.py runserver
```

### 2. Frontend React
```bash
cd frontend
npm install
npm run dev
```

### 3. Base de Datos
```bash
docker-compose up -d db redis phpmyadmin
```

## 🏢 Configuración Empresa

### Datos de Empresa Demo
- **RUC:** 20123456789
- **Razón Social:** EMPRESA DEMO FELICITA SAC
- **Dirección:** AV. JAVIER PRADO ESTE 123, SAN ISIDRO, LIMA

### Series de Comprobante
- **Facturas:** F001
- **Boletas:** B001
- **Notas de Crédito:** FC01
- **Notas de Débito:** FD01

## 🎯 Funcionalidades Implementadas

### ✅ Backend Completado
- [x] Configuración Django con MySQL
- [x] Modelos Core (Empresa, Cliente, Configuración)
- [x] Autenticación JWT
- [x] API REST con DRF
- [x] Admin Django configurado
- [x] Validaciones SUNAT (RUC, DNI)
- [x] Fixtures con datos iniciales

### ✅ Frontend Completado
- [x] React 18 + TypeScript
- [x] Autenticación JWT
- [x] Dashboard principal
- [x] Layout responsivo
- [x] Navegación entre módulos
- [x] Tailwind CSS configurado

### ⏳ Próximas Fases
- [ ] Facturación electrónica completa
- [ ] Punto de venta funcional
- [ ] Control inventarios PEPS
- [ ] Reportes PLE SUNAT
- [ ] Integración Nubefact

## 🐛 Solución de Problemas

### Error de Base de Datos
```bash
docker-compose restart db
python manage.py migrate
```

### Error de Dependencias Frontend
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error de Permisos Linux
```bash
chmod +x iniciar-desarrollo.sh
sudo chown -R $USER:$USER .
```

## 📞 Soporte

- **Email:** soporte@felicita.pe
- **GitHub:** https://github.com/macgonzales94/felicita
- **Issues:** https://github.com/macgonzales94/felicita/issues

---

# ARCHIVO: config/__init__.py

"""
FELICITA - Configuración Principal
Sistema de Facturación Electrónica para Perú
"""

---

# ARCHIVO: felicita/__init__.py (backend/felicita/__init__.py)

"""
FELICITA - Proyecto Principal Django
Sistema de Facturación Electrónica para Perú
"""

---

# ARCHIVO: sql/init.sql

-- FELICITA - Inicialización Base de Datos MySQL
-- Sistema de Facturación Electrónica para Perú

CREATE DATABASE IF NOT EXISTS felicita_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'felicita_user'@'%' IDENTIFIED BY 'dev_password_123';
GRANT ALL PRIVILEGES ON felicita_db.* TO 'felicita_user'@'%';
FLUSH PRIVILEGES;

USE felicita_db;

-- Configuraciones específicas para FELICITA
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';
SET time_zone = '-05:00';

---

# ARCHIVO: frontend/public/vite.svg

<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--logos" width="31.88" height="32" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 257"><defs><linearGradient id="IconifyId1813088fe1fbc01fb466" x1="-.828%" x2="57.636%" y1="7.652%" y2="78.411%"><stop offset="0%" stop-color="#41D1FF"></stop><stop offset="100%" stop-color="#BD34FE"></stop></linearGradient><linearGradient id="IconifyId1813088fe1fbc01fb467" x1="43.376%" x2="50.316%" y1="2.242%" y2="89.03%"><stop offset="0%" stop-color="#FFEA83"></stop><stop offset="8.333%" stop-color="#FFDD35"></stop><stop offset="100%" stop-color="#FFA800"></stop></linearGradient></defs><path fill="url(#IconifyId1813088fe1fbc01fb466)" d="M255.153 37.938L134.897 252.976c-2.483 4.44-8.862 4.466-11.382.048L.875 37.958c-2.746-4.814 1.371-10.646 6.827-9.67l120.385 21.517a6.537 6.537 0 0 0 2.322-.004l117.867-21.483c5.438-.991 9.574 4.796 6.877 9.62Z"></path><path fill="url(#IconifyId1813088fe1fbc01fb467)" d="M185.432.063L96.44 17.501a3.268 3.268 0 0 0-2.634 3.014l-5.474 92.456a3.268 3.268 0 0 0 3.997 3.378l24.777-5.718c2.318-.535 4.413 1.507 3.936 3.838l-7.361 36.047c-.495 2.426 1.782 4.5 4.151 3.78l15.304-4.649c2.372-.72 4.652 1.36 4.15 3.788l-11.698 56.621c-.732 3.542 3.979 5.473 5.943 2.437l1.313-2.028l72.516-144.72c1.215-2.423-.88-5.186-3.54-4.672l-25.505 4.922c-2.396.462-4.435-1.77-3.759-4.114l16.646-57.705c.677-2.35-1.37-4.583-3.769-4.113Z"></path></svg>

---

# ARCHIVO: tsconfig.node.json (frontend/tsconfig.node.json)

{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}