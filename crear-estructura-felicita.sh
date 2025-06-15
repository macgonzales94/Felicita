#!/bin/bash

# Script para crear la estructura completa del proyecto FELICITA
# Para sistemas Linux
# Ejecutar con: chmod +x crear_estructura_felicita.sh && ./crear_estructura_felicita.sh

echo "🚀 Creando estructura del proyecto FELICITA..."

# Crear directorio principal del proyecto
mkdir -p felicita
cd felicita

# Crear archivos raíz
touch README.md
touch docker-compose.yml
touch .env.example
touch .gitignore
touch iniciar-desarrollo.sh
touch iniciar-desarrollo.bat
touch CONOCIMIENTO_BASE.md

echo "📁 Creados archivos raíz del proyecto"

# Crear estructura del Backend
echo "🔧 Creando estructura del Backend..."

# Directorio principal backend
mkdir -p backend

# Archivos principales backend
touch backend/manage.py
touch backend/requirements.txt

# Directorio requirements
mkdir -p backend/requirements
touch backend/requirements/base.txt
touch backend/requirements/local.txt
touch backend/requirements/produccion.txt

# Directorio config
mkdir -p backend/config
touch backend/config/__init__.py
touch backend/config/urls.py
touch backend/config/wsgi.py
touch backend/config/asgi.py

# Subdirectorio config/settings
mkdir -p backend/config/settings
touch backend/config/settings/__init__.py
touch backend/config/settings/base.py
touch backend/config/settings/local.py
touch backend/config/settings/produccion.py
touch backend/config/settings/testing.py

# Directorio aplicaciones
mkdir -p backend/aplicaciones
touch backend/aplicaciones/__init__.py

# Aplicación core
mkdir -p backend/aplicaciones/core
touch backend/aplicaciones/core/__init__.py
touch backend/aplicaciones/core/models.py
touch backend/aplicaciones/core/serializers.py
touch backend/aplicaciones/core/views.py
touch backend/aplicaciones/core/urls.py
touch backend/aplicaciones/core/admin.py
touch backend/aplicaciones/core/apps.py
mkdir -p backend/aplicaciones/core/migrations
touch backend/aplicaciones/core/migrations/__init__.py

# Aplicación usuarios
mkdir -p backend/aplicaciones/usuarios
touch backend/aplicaciones/usuarios/__init__.py
touch backend/aplicaciones/usuarios/models.py
touch backend/aplicaciones/usuarios/serializers.py
touch backend/aplicaciones/usuarios/views.py
touch backend/aplicaciones/usuarios/urls.py
touch backend/aplicaciones/usuarios/admin.py
touch backend/aplicaciones/usuarios/apps.py
mkdir -p backend/aplicaciones/usuarios/migrations
touch backend/aplicaciones/usuarios/migrations/__init__.py

# Aplicación facturación
mkdir -p backend/aplicaciones/facturacion
touch backend/aplicaciones/facturacion/__init__.py
touch backend/aplicaciones/facturacion/models.py
touch backend/aplicaciones/facturacion/serializers.py
touch backend/aplicaciones/facturacion/views.py
touch backend/aplicaciones/facturacion/urls.py
touch backend/aplicaciones/facturacion/services.py
touch backend/aplicaciones/facturacion/admin.py
touch backend/aplicaciones/facturacion/apps.py
mkdir -p backend/aplicaciones/facturacion/migrations
touch backend/aplicaciones/facturacion/migrations/__init__.py

# Aplicación inventario
mkdir -p backend/aplicaciones/inventario
touch backend/aplicaciones/inventario/__init__.py
touch backend/aplicaciones/inventario/models.py
touch backend/aplicaciones/inventario/serializers.py
touch backend/aplicaciones/inventario/views.py
touch backend/aplicaciones/inventario/urls.py
touch backend/aplicaciones/inventario/services.py
touch backend/aplicaciones/inventario/admin.py
touch backend/aplicaciones/inventario/apps.py
mkdir -p backend/aplicaciones/inventario/migrations
touch backend/aplicaciones/inventario/migrations/__init__.py

# Aplicación contabilidad
mkdir -p backend/aplicaciones/contabilidad
touch backend/aplicaciones/contabilidad/__init__.py
touch backend/aplicaciones/contabilidad/models.py
touch backend/aplicaciones/contabilidad/serializers.py
touch backend/aplicaciones/contabilidad/views.py
touch backend/aplicaciones/contabilidad/urls.py
touch backend/aplicaciones/contabilidad/services.py
touch backend/aplicaciones/contabilidad/admin.py
touch backend/aplicaciones/contabilidad/apps.py
mkdir -p backend/aplicaciones/contabilidad/migrations
touch backend/aplicaciones/contabilidad/migrations/__init__.py

# Aplicación integraciones
mkdir -p backend/aplicaciones/integraciones
touch backend/aplicaciones/integraciones/__init__.py
touch backend/aplicaciones/integraciones/models.py
touch backend/aplicaciones/integraciones/views.py
touch backend/aplicaciones/integraciones/urls.py
touch backend/aplicaciones/integraciones/admin.py
touch backend/aplicaciones/integraciones/apps.py

# Subdirectorio services en integraciones
mkdir -p backend/aplicaciones/integraciones/services
touch backend/aplicaciones/integraciones/services/__init__.py
touch backend/aplicaciones/integraciones/services/nubefact.py
touch backend/aplicaciones/integraciones/services/apis_peru.py

mkdir -p backend/aplicaciones/integraciones/migrations
touch backend/aplicaciones/integraciones/migrations/__init__.py

# Aplicación punto_venta
mkdir -p backend/aplicaciones/punto_venta
touch backend/aplicaciones/punto_venta/__init__.py
touch backend/aplicaciones/punto_venta/models.py
touch backend/aplicaciones/punto_venta/serializers.py
touch backend/aplicaciones/punto_venta/views.py
touch backend/aplicaciones/punto_venta/urls.py
touch backend/aplicaciones/punto_venta/admin.py
touch backend/aplicaciones/punto_venta/apps.py
mkdir -p backend/aplicaciones/punto_venta/migrations
touch backend/aplicaciones/punto_venta/migrations/__init__.py

# Aplicación reportes
mkdir -p backend/aplicaciones/reportes
touch backend/aplicaciones/reportes/__init__.py
touch backend/aplicaciones/reportes/models.py
touch backend/aplicaciones/reportes/serializers.py
touch backend/aplicaciones/reportes/views.py
touch backend/aplicaciones/reportes/urls.py
touch backend/aplicaciones/reportes/services.py
touch backend/aplicaciones/reportes/admin.py
touch backend/aplicaciones/reportes/apps.py
mkdir -p backend/aplicaciones/reportes/migrations
touch backend/aplicaciones/reportes/migrations/__init__.py

# Directorio fixtures
mkdir -p backend/fixtures
touch backend/fixtures/usuarios_iniciales.json
touch backend/fixtures/plan_cuentas_pcge.json
touch backend/fixtures/productos_ejemplo.json
touch backend/fixtures/clientes_ejemplo.json
touch backend/fixtures/series_comprobantes.json
touch backend/fixtures/datos_iniciales.json

# Directorio static
mkdir -p backend/static/css
mkdir -p backend/static/js
mkdir -p backend/static/img
mkdir -p backend/static/admin

# Directorio media
mkdir -p backend/media/comprobantes
mkdir -p backend/media/reportes
mkdir -p backend/media/uploads

# Directorio logs
mkdir -p backend/logs
touch backend/logs/django.log
touch backend/logs/nubefact.log
touch backend/logs/auditoria.log

echo "✅ Estructura del Backend creada exitosamente"

# Crear estructura del Frontend
echo "⚛️ Creando estructura del Frontend..."

# Directorio principal frontend
mkdir -p frontend

# Archivos principales frontend
touch frontend/package.json
touch frontend/package-lock.json
touch frontend/tsconfig.json
touch frontend/tailwind.config.js
touch frontend/vite.config.ts
touch frontend/postcss.config.js
touch frontend/index.html

# Directorio public
mkdir -p frontend/public
touch frontend/public/favicon.ico
touch frontend/public/logo-felicita.png

# Directorio src
mkdir -p frontend/src
touch frontend/src/main.tsx
touch frontend/src/App.tsx
touch frontend/src/vite-env.d.ts

# Directorio componentes
mkdir -p frontend/src/componentes

# Subdirectorio componentes/comunes
mkdir -p frontend/src/componentes/comunes
touch frontend/src/componentes/comunes/Header.tsx
touch frontend/src/componentes/comunes/Sidebar.tsx
touch frontend/src/componentes/comunes/Footer.tsx
touch frontend/src/componentes/comunes/Cargando.tsx
touch frontend/src/componentes/comunes/MensajeError.tsx

# Subdirectorio componentes/formularios
mkdir -p frontend/src/componentes/formularios
touch frontend/src/componentes/formularios/FormularioCliente.tsx
touch frontend/src/componentes/formularios/FormularioFactura.tsx
touch frontend/src/componentes/formularios/FormularioProducto.tsx

# Subdirectorio componentes/ui
mkdir -p frontend/src/componentes/ui
touch frontend/src/componentes/ui/button.tsx
touch frontend/src/componentes/ui/card.tsx
touch frontend/src/componentes/ui/input.tsx
touch frontend/src/componentes/ui/modal.tsx
touch frontend/src/componentes/ui/index.ts

# Directorio paginas
mkdir -p frontend/src/paginas
touch frontend/src/paginas/Login.tsx
touch frontend/src/paginas/Dashboard.tsx
touch frontend/src/paginas/PuntoDeVenta.tsx
touch frontend/src/paginas/Facturacion.tsx
touch frontend/src/paginas/Inventario.tsx
touch frontend/src/paginas/Clientes.tsx
touch frontend/src/paginas/Productos.tsx
touch frontend/src/paginas/Reportes.tsx
touch frontend/src/paginas/Configuracion.tsx

# Directorio contextos
mkdir -p frontend/src/contextos
touch frontend/src/contextos/AuthContext.tsx
touch frontend/src/contextos/FacturacionContext.tsx
touch frontend/src/contextos/AppContext.tsx

# Directorio servicios
mkdir -p frontend/src/servicios
touch frontend/src/servicios/api.ts
touch frontend/src/servicios/auth.ts
touch frontend/src/servicios/facturas.ts
touch frontend/src/servicios/productos.ts
touch frontend/src/servicios/clientes.ts
touch frontend/src/servicios/inventario.ts
touch frontend/src/servicios/reportes.ts

# Directorio types
mkdir -p frontend/src/types
touch frontend/src/types/index.ts
touch frontend/src/types/auth.ts
touch frontend/src/types/factura.ts
touch frontend/src/types/producto.ts
touch frontend/src/types/cliente.ts
touch frontend/src/types/common.ts

# Directorio hooks
mkdir -p frontend/src/hooks
touch frontend/src/hooks/useAuth.ts
touch frontend/src/hooks/useApi.ts
touch frontend/src/hooks/useLocalStorage.ts
touch frontend/src/hooks/useDebounce.ts

# Directorio utils
mkdir -p frontend/src/utils
touch frontend/src/utils/validaciones.ts
touch frontend/src/utils/formatos.ts
touch frontend/src/utils/constantes.ts
touch frontend/src/utils/helpers.ts
touch frontend/src/utils/storage.ts

# Directorio estilos
mkdir -p frontend/src/estilos
touch frontend/src/estilos/globals.css
touch frontend/src/estilos/dashboard.css
touch frontend/src/estilos/punto-venta.css

# Directorio dist (se genera automáticamente, pero lo creamos por completitud)
mkdir -p frontend/dist

echo "✅ Estructura del Frontend creada exitosamente"

# Crear estructura de Documentación
echo "📚 Creando estructura de Documentación..."

mkdir -p documentacion
touch documentacion/INSTALACION.md
touch documentacion/API.md
touch documentacion/ARQUITECTURA.md
touch documentacion/DEPLOYMENT.md
touch documentacion/MANUAL_USUARIO.md
touch documentacion/DEVELOPMENT.md
touch documentacion/TESTING.md

echo "✅ Estructura de Documentación creada exitosamente"

# Crear estructura de Scripts
echo "🔨 Creando estructura de Scripts..."

mkdir -p scripts
touch scripts/backup_db.py
touch scripts/deploy.sh
touch scripts/reset_db.sh
touch scripts/load_fixtures.py

# Hacer ejecutables los scripts shell
chmod +x scripts/deploy.sh
chmod +x scripts/reset_db.sh
chmod +x iniciar-desarrollo.sh

echo "✅ Estructura de Scripts creada exitosamente"

# Crear estructura de Tests
echo "🧪 Creando estructura de Tests..."

mkdir -p tests/backend
mkdir -p tests/frontend
mkdir -p tests/integration
mkdir -p tests/e2e

echo "✅ Estructura de Tests creada exitosamente"

# Mostrar resumen
echo ""
echo "🎉 ¡ESTRUCTURA DEL PROYECTO FELICITA CREADA EXITOSAMENTE!"
echo ""
echo "📁 Estructura creada:"
echo "   ├── 📁 backend/ (Django + Django REST Framework)"
echo "   ├── 📁 frontend/ (React + TypeScript + Vite)"
echo "   ├── 📁 documentacion/ (Manuales y guías)"
echo "   ├── 📁 scripts/ (Scripts de utilidad)"
echo "   └── 📁 tests/ (Pruebas del sistema)"
echo ""
echo "📊 Estadísticas:"
echo "   🗂️  Directorios creados: $(find . -type d | wc -l)"
echo "   📄 Archivos creados: $(find . -type f | wc -l)"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. cd felicita"
echo "   2. Revisar y editar .env.example"
echo "   3. Ejecutar ./iniciar-desarrollo.sh"
echo ""
echo "📖 Para más información consulta CONOCIMIENTO_BASE.md"
echo ""
echo "✨ ¡Feliz desarrollo con FELICITA!"