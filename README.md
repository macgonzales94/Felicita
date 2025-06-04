# 🚀 FELICITA - Sistema de Facturación Electrónica para Perú

**FELICITA** es un sistema completo de facturación electrónica que cumple con la normativa SUNAT peruana, incluyendo punto de venta, control de inventarios, contabilidad automática y reportes.

## 📋 Características Principales

### ✅ Facturación Electrónica SUNAT
- ✨ Emisión de facturas, boletas, notas de crédito/débito
- 🔌 Integración con Nubefact API (OSE certificado)
- 📄 Generación automática de XML UBL 2.1
- 🔍 Códigos QR y validación SUNAT
- 📊 Numeración correlativa obligatoria

### 🏪 Punto de Venta (POS)
- 📱 Interfaz táctil optimizada
- 🛒 Carrito de compras en tiempo real
- 💳 Múltiples métodos de pago
- 🖨️ Impresión automática de comprobantes
- 📷 Soporte para códigos de barras

### 📦 Control de Inventarios
- 📈 Método PEPS (obligatorio SUNAT)
- 🏢 Múltiples almacenes
- ⚡ Control de stock en tiempo real
- 🔔 Alertas de stock mínimo
- 📋 Kardex automatizado

### 💰 Contabilidad Automática
- 📚 Plan de cuentas PCGE
- ⚙️ Asientos contables automáticos
- 📈 Estados financieros básicos
- 💸 Cuentas por cobrar y pagar
- 🔄 Conciliaciones bancarias

### 📊 Reportes y Analytics
- 📋 Dashboard ejecutivo con KPIs
- 📑 Reportes PLE para SUNAT
- 📈 Análisis de ventas
- 📊 Gráficos interactivos
- 📤 Exportación Excel/PDF

## 🏗️ Arquitectura Técnica

### Stack Tecnológico
- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Base de Datos:** PostgreSQL
- **Cache:** Redis
- **Integración:** Nubefact API
- **Desarrollo:** Docker para PostgreSQL local

### Estructura del Proyecto
```
felicita/
├── backend/                 # Django Backend
│   ├── felicita/           # Proyecto principal
│   ├── aplicaciones/       # Apps Django
│   │   ├── autenticacion/  # Usuarios y permisos
│   │   ├── empresas/       # Datos de empresas
│   │   ├── clientes/       # Gestión de clientes
│   │   ├── productos/      # Catálogo de productos
│   │   ├── inventarios/    # Control de stock
│   │   ├── facturacion/    # Facturación electrónica
│   │   ├── contabilidad/   # Contabilidad automática
│   │   ├── reportes/       # Reportes y analytics
│   │   └── configuracion/  # Configuraciones sistema
│   ├── configuracion/      # Settings Django
│   ├── fixtures/           # Datos iniciales
│   └── requirements.txt    # Dependencias Python
├── frontend/               # React Frontend (próximamente)
├── docker-compose.yml      # PostgreSQL + Redis local
├── .env.example           # Variables de entorno
├── iniciar-desarrollo.sh  # Script inicio Linux/Mac
├── iniciar-desarrollo.bat # Script inicio Windows
└── README.md              # Esta documentación
```

## 🚀 Inicio Rápido

### Prerrequisitos
- **Python 3.8+** instalado
- **Docker** y **Docker Compose** instalados
- **Node.js 16+** (para frontend, opcional)
- **Git** para clonar el repositorio

### Instalación en Linux/Mac

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/felicita.git
cd felicita

# 2. Dar permisos de ejecución al script
chmod +x iniciar-desarrollo.sh

# 3. Ejecutar script de configuración automática
./iniciar-desarrollo.sh

# 4. Iniciar el servidor Django
cd backend
source ../venv/bin/activate
python manage.py runserver
```

### Instalación en Windows

```cmd
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/felicita.git
cd felicita

# 2. Ejecutar script de configuración automática
iniciar-desarrollo.bat

# 3. Iniciar el servidor Django
cd backend
venv\Scripts\activate.bat
python manage.py runserver
```

### Configuración Manual (Alternativa)

```bash
# 1. Crear archivo de entorno
cp .env.example .env

# 2. Iniciar servicios Docker
docker-compose up -d

# 3. Crear entorno virtual Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate.bat  # Windows

# 4. Instalar dependencias
cd backend
pip install -r requirements.txt

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Cargar datos iniciales
python manage.py setup_felicita

# 7. Crear superusuario (opcional)
python manage.py createsuperuser

# 8. Iniciar servidor
python manage.py runserver
```

## 🌐 Acceso al Sistema

Una vez configurado, el sistema estará disponible en:

### URLs Principales
- **Admin Django:** http://localhost:8000/admin/
- **API REST:** http://localhost:8000/api/
- **Documentación API:** http://localhost:8000/api/docs/
- **Frontend React:** http://localhost:3000/ *(próximamente)*

### Credenciales por Defecto
- **Usuario:** `admin`
- **Contraseña:** `admin123`

### Datos de Prueba Incluidos
- ✅ **Empresa demo:** EMPRESA DEMO FELICITA SAC (RUC: 20123456789)
- ✅ **Clientes de prueba:** Con RUCs y DNIs válidos
- ✅ **Productos demo:** Laptops, servicios, artículos de oficina
- ✅ **Plan contable PCGE:** Cuentas básicas configuradas
- ✅ **Series de comprobantes:** F001, B001, FC01, etc.

## ⚙️ Configuración Avanzada

### Variables de Entorno Importantes

```bash
# Base de Datos
DATABASE_URL=postgresql://felicita_user:password@localhost:5432/felicita_db

# Nubefact (Facturación Electrónica)
NUBEFACT_TOKEN=tu_token_demo
NUBEFACT_RUC_EMISOR=20123456789
NUBEFACT_MODO=DEMO  # DEMO o PRODUCCION

# APIs Perú (Validaciones)
RENIEC_API_KEY=tu_api_key_reniec
SUNAT_API_KEY=tu_api_key_sunat

# Configuración de Desarrollo
DEBUG=True
SECRET_KEY=tu_clave_secreta_desarrollo
```

### Configuración de Nubefact

Para usar facturación electrónica real:

1. **Registrarse en Nubefact:** https://nubefact.com/
2. **Obtener credenciales** de API
3. **Configurar en .env:**
   ```bash
   NUBEFACT_TOKEN=tu_token_real
   NUBEFACT_RUC_EMISOR=tu_ruc_empresa
   NUBEFACT_USUARIO_SOL=tu_usuario_sol
   NUBEFACT_CLAVE_SOL=tu_clave_sol
   NUBEFACT_MODO=PRODUCCION
   ```

### Configuración de APIs Perú

Para validaciones automáticas de RUC/DNI:

1. **Registrarse en APIs Perú:** https://apis.net.pe/
2. **Obtener tokens** de RENIEC y SUNAT
3. **Configurar en .env:**
   ```bash
   RENIEC_API_KEY=tu_token_reniec
   SUNAT_API_KEY=tu_token_sunat
   ```

## 🛠️ Comandos Útiles

### Gestión de la Base de Datos
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Resetear datos iniciales
python manage.py setup_felicita --reset

# Backup de la base de datos
docker exec felicita_db pg_dump -U felicita_user felicita_db > backup.sql

# Restaurar backup
docker exec -i felicita_db psql -U felicita_user felicita_db < backup.sql
```

### Desarrollo y Testing
```bash
# Ejecutar tests
python manage.py test

# Shell de Django
python manage.py shell

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Ver logs en tiempo real
tail -f logs/felicita.log
```

### Docker
```bash
# Iniciar servicios
docker-compose up -d

# Parar servicios
docker-compose down

# Ver logs de PostgreSQL
docker logs felicita_db

# Acceder a PostgreSQL
docker exec -it felicita_db psql -U felicita_user felicita_db

# Reiniciar servicios
docker-compose restart
```

## 📚 Guías de Uso

### 1. Configurar Primera Empresa
1. Acceder al admin: http://localhost:8000/admin/
2. Ir a **Empresas** → **Empresas**
3. Editar la empresa demo o crear nueva
4. Completar datos reales: RUC, razón social, dirección
5. Configurar credenciales SOL de SUNAT

### 2. Crear Primeros Productos
1. Ir a **Productos** → **Categoría productos** (crear categorías)
2. Ir a **Productos** → **Productos** (crear productos)
3. Completar: código, nombre, precios, stock
4. Asignar categoría y unidad de medida

### 3. Registrar Clientes
1. Ir a **Clientes** → **Clientes**
2. Completar datos del cliente
3. Validar RUC/DNI según tipo
4. Configurar límite de crédito si aplica

### 4. Emitir Primera Factura
1. Usar la API REST o admin
2. Seleccionar serie de comprobante
3. Agregar cliente y productos
4. El sistema calculará IGV automáticamente
5. Se generará XML y enviará a SUNAT (si está configurado)

### 5. Configurar Punto de Venta
1. Configurar almacén principal
2. Ingresar stock inicial de productos
3. Configurar series de boletas (B001)
4. *(Frontend React se desarrollará en próximas fases)*

## 🇵🇪 Cumplimiento Normativo Peruano

### Requisitos SUNAT Implementados
- ✅ **Facturación electrónica obligatoria**
- ✅ **Numeración correlativa sin vacíos**
- ✅ **Formato XML UBL 2.1**
- ✅ **IGV 18% automático**
- ✅ **Método PEPS para inventarios**
- ✅ **Plan de cuentas PCGE**
- ✅ **Validación de RUC con algoritmo verificador**
- ✅ **Preparado para libros electrónicos PLE**

### Tipos de Comprobante Soportados
- **01:** Factura
- **03:** Boleta de Venta
- **07:** Nota de Crédito
- **08:** Nota de Débito
- **09:** Guía de Remisión *(próximamente)*

### Validaciones Automáticas
- ✅ **RUC:** 11 dígitos con verificador
- ✅ **DNI:** 8 dígitos numéricos
- ✅ **Correlatividad** de comprobantes
- ✅ **Integridad contable** (debe = haber)
- ✅ **Stock suficiente** para ventas

## 🔧 Resolución de Problemas

### Error de Conexión a PostgreSQL
```bash
# Verificar que Docker esté ejecutándose
docker ps

# Reiniciar contenedor de PostgreSQL
docker-compose restart postgres_felicita

# Verificar logs
docker logs felicita_db
```

### Error de Migraciones Django
```bash
# Resetear migraciones (¡Cuidado en producción!)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

### Error de Dependencias Python
```bash
# Actualizar pip
pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Problemas con Nubefact
1. Verificar que el token sea válido
2. Confirmar que el RUC esté registrado en Nubefact
3. Revisar logs: `tail -f logs/felicita.log`
4. Usar modo DEMO para pruebas

## 🚦 Roadmap de Desarrollo

### ✅ Fase 1: Arquitectura y Base de Datos (Completada)
- [x] Configuración Django + PostgreSQL
- [x] Modelos completos en español
- [x] Datos iniciales y fixtures
- [x] Scripts de desarrollo local

### 🚧 Fase 2: Autenticación y Seguridad (Próxima)
- [ ] Sistema de usuarios y roles
- [ ] JWT tokens para API
- [ ] Permisos granulares por módulo
- [ ] Auditoría de cambios

### 📅 Fase 3: API Core y Nubefact (Semanas 3-4)
- [ ] APIs REST completas
- [ ] Integración Nubefact funcional
- [ ] Validaciones RUC/DNI online
- [ ] Generación de XML UBL

### 📅 Fase 4: Punto de Venta Frontend (Semana 5)
- [ ] Interface React optimizada
- [ ] Carrito de compras táctil
- [ ] Búsqueda de productos
- [ ] Impresión de comprobantes

### 📅 Fase 5: Dashboard y Reportes (Semanas 6-7)
- [ ] Dashboard ejecutivo
- [ ] Gráficos interactivos
- [ ] Reportes PLE SUNAT
- [ ] Exportación Excel/PDF

### 📅 Fase 6: Gestión Administrativa (Semana 8)
- [ ] Formularios de administración
- [ ] Importación masiva Excel
- [ ] Configuraciones avanzadas
- [ ] Backup automático

### 📅 Fase 7: Deployment y Optimización (Semana 9)
- [ ] Configuración producción
- [ ] Optimización de performance
- [ ] Monitoreo y logging
- [ ] SSL y seguridad

### 📅 Fase 8: Documentación y Testing (Semana 10)
- [ ] Tests unitarios completos
- [ ] Documentación de usuario
- [ ] Videos tutoriales
- [ ] Manual de instalación

## 💡 Contribuir al Proyecto

### Reportar Problemas
1. Buscar en issues existentes
2. Crear nuevo issue con:
   - Descripción detallada
   - Pasos para reproducir
   - Logs de error
   - Información del entorno

### Enviar Contribuciones
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "Agregar nueva funcionalidad"`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código
- **Todo en español:** variables, clases, comentarios
- **PEP 8** para Python
- **Prettier** para TypeScript/React
- **Tests** para funcionalidades críticas
- **Documentación** para APIs

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Soporte y Comunidad

### Soporte Técnico
- **Email:** soporte@felicita.pe
- **GitHub Issues:** Para reportar bugs
- **Documentación:** Wiki del repositorio

### Comunidad
- **Discord:** [Servidor FELICITA](https://discord.gg/felicita)
- **Telegram:** @FelicitaPeru
- **YouTube:** Tutoriales y demos

## 🏆 Reconocimientos

FELICITA fue desarrollado específicamente para el mercado peruano, cumpliendo con todas las normativas SUNAT vigentes. Agradecemos a la comunidad de desarrolladores peruanos que contribuyen al ecosistema de facturación electrónica.

---

## 🎯 ¿Listo para empezar?

```bash
git clone https://github.com/tu-usuario/felicita.git
cd felicita
./iniciar-desarrollo.sh  # Linux/Mac
# o
iniciar-desarrollo.bat   # Windows
```

¡Bienvenido a FELICITA! 🚀 El futuro de la facturación electrónica peruana está aquí.

---

**FELICITA** - *Sistema de Facturación Electrónica para Perú*  
📧 contacto@felicita.pe | 🌐 https://felicita.pe
