#!/bin/bash

# ==============================================
# SCRIPT DE INICIO DESARROLLO - FELICITA
# Para Linux/Mac - Sistema de Facturación Perú
# ==============================================

echo "🚀 Iniciando entorno de desarrollo FELICITA..."

# Verificar que Docker esté corriendo
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# Verificar que Node.js esté instalado
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js no está instalado. Descarga desde https://nodejs.org/"
    exit 1
fi

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📄 Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado. Puedes editarlo si necesitas cambiar configuraciones."
fi

# Levantar servicios Docker (PostgreSQL y Redis)
echo "🐳 Levantando servicios Docker (PostgreSQL y Redis)..."
docker-compose up -d

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
timeout=60
while ! docker exec felicita_postgres pg_isready -U felicita_user -d felicita_db &> /dev/null; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo "❌ Error: PostgreSQL no está respondiendo después de 60 segundos."
        exit 1
    fi
done
echo "✅ PostgreSQL está listo!"

# Configurar Backend Django
echo "🐍 Configurando Backend Django..."
cd backend

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual Python..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones de base de datos..."
python manage.py makemigrations
python manage.py migrate

# Cargar datos iniciales
echo "📊 Cargando datos iniciales..."
python manage.py loaddata fixtures/plan_cuentas.json
python manage.py loaddata fixtures/series_comprobantes.json
python manage.py loaddata fixtures/usuarios_demo.json
python manage.py loaddata fixtures/clientes_demo.json
python manage.py loaddata fixtures/productos_demo.json

# Crear superusuario si no existe
echo "👤 Creando usuario administrador..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
from aplicaciones.usuarios.models import Usuario
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    usuario = User.objects.create_user(
        username='admin',
        email='admin@felicita.pe',
        password='admin123',
        first_name='Administrador',
        last_name='FELICITA'
    )
    print('✅ Usuario admin creado: admin/admin123')
else:
    print('ℹ️ Usuario admin ya existe')
"

# Regresar al directorio raíz
cd ..

# Configurar Frontend React
echo "⚛️ Configurando Frontend React..."
cd frontend

# Instalar dependencias de Node.js
if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependencias Node.js..."
    npm install
fi

cd ..

# Mostrar información final
echo ""
echo "🎉 ¡Entorno de desarrollo FELICITA configurado correctamente!"
echo ""
echo "📋 COMANDOS PARA DESARROLLAR:"
echo "   Backend Django:  cd backend && source venv/bin/activate && python manage.py runserver"
echo "   Frontend React:  cd frontend && npm run dev"
echo ""
echo "🌐 URLs DE DESARROLLO:"
echo "   Backend API:     http://localhost:8000"
echo "   Admin Django:    http://localhost:8000/admin"
echo "   Frontend React:  http://localhost:3000 (o 5173)"
echo ""
echo "👤 CREDENCIALES DEMO:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "🗄️ BASE DE DATOS:"
echo "   Host: localhost:5432"
echo "   DB: felicita_db"
echo "   User: felicita_user"
echo "   Pass: felicita_password_2024"
echo ""
echo "📚 DOCUMENTACIÓN: Ver README.md para más detalles"
echo ""

# Función para abrir ambos servicios
read -p "¿Deseas iniciar automáticamente Backend y Frontend? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Iniciando servicios..."
    
    # Abrir terminal para Backend
    osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/backend && source venv/bin/activate && python manage.py runserver"' 2>/dev/null || \
    gnome-terminal -- bash -c "cd $(pwd)/backend && source venv/bin/activate && python manage.py runserver; exec bash" 2>/dev/null || \
    echo "⚠️ Ejecuta manualmente: cd backend && source venv/bin/activate && python manage.py runserver"
    
    sleep 2
    
    # Abrir terminal para Frontend
    osascript -e 'tell app "Terminal" to do script "cd '$(pwd)'/frontend && npm run dev"' 2>/dev/null || \
    gnome-terminal -- bash -c "cd $(pwd)/frontend && npm run dev; exec bash" 2>/dev/null || \
    echo "⚠️ Ejecuta manualmente: cd frontend && npm run dev"
    
    echo "✅ Servicios iniciados en terminales separadas"
else
    echo "ℹ️ Servicios no iniciados automáticamente"
fi

echo "🎯 ¡FELICITA está listo para desarrollar!"