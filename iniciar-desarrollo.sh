#!/bin/bash

# FELICITA - Script de Inicio Desarrollo (Linux/Mac)
# Autor: Equipo FELICITA
# Descripción: Inicia todo el entorno de desarrollo automáticamente

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner FELICITA
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    ███████╗███████╗██╗     ██╗ ██████╗██╗████████╗ █████╗    ║"
echo "║    ██╔════╝██╔════╝██║     ██║██╔════╝██║╚══██╔══╝██╔══██╗   ║"
echo "║    █████╗  █████╗  ██║     ██║██║     ██║   ██║   ███████║   ║"
echo "║    ██╔══╝  ██╔══╝  ██║     ██║██║     ██║   ██║   ██╔══██║   ║"
echo "║    ██║     ███████╗███████╗██║╚██████╗██║   ██║   ██║  ██║   ║"
echo "║    ╚═╝     ╚══════╝╚══════╝╚═╝ ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝   ║"
echo "║                                                              ║"
echo "║           Sistema de Facturación Electrónica Perú           ║"
echo "║                    Iniciando Desarrollo...                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Función para mostrar mensajes con estilo
show_message() {
    echo -e "${CYAN}[FELICITA]${NC} $1"
}

show_success() {
    echo -e "${GREEN}✓ [ÉXITO]${NC} $1"
}

show_warning() {
    echo -e "${YELLOW}⚠ [ADVERTENCIA]${NC} $1"
}

show_error() {
    echo -e "${RED}✗ [ERROR]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    show_error "No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto FELICITA."
    exit 1
fi

show_message "Verificando requisitos del sistema..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    show_error "Docker no está instalado. Por favor instala Docker desde https://docker.com"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    show_error "Docker Compose no está instalado."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    show_error "Node.js no está instalado. Por favor instala Node.js desde https://nodejs.org"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    show_error "Python 3 no está instalado."
    exit 1
fi

show_success "Todos los requisitos están instalados"

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    show_message "Creando archivo .env desde .env.example..."
    cp .env.example .env
    show_success "Archivo .env creado. Puedes modificar las variables si es necesario."
fi

# Crear directorios necesarios
show_message "Creando directorios necesarios..."
mkdir -p backend/logs
mkdir -p backend/media/comprobantes
mkdir -p backend/media/reportes
mkdir -p backend/media/uploads
mkdir -p backend/static
mkdir -p sql
show_success "Directorios creados"

# Parar contenedores existentes
show_message "Parando contenedores existentes..."
docker-compose down

# Iniciar servicios de base de datos
show_message "Iniciando servicios de base de datos (MySQL + Redis + phpMyAdmin)..."
docker-compose up -d db redis phpmyadmin

# Esperar a que MySQL esté listo
show_message "Esperando a que MySQL esté listo..."
until docker-compose exec -T db mysqladmin ping -h"localhost" --silent; do
    echo -n "."
    sleep 2
done
echo ""
show_success "MySQL está listo"

# Configurar entorno virtual Python
show_message "Configurando entorno virtual Python..."
cd backend

# Crear virtual environment si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
    show_success "Virtual environment creado"
fi

# Activar virtual environment
source venv/bin/activate
show_success "Virtual environment activado"

# Instalar dependencias Python
show_message "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt
show_success "Dependencias Python instaladas"

# Ejecutar migraciones
show_message "Ejecutando migraciones de Django..."
python manage.py makemigrations
python manage.py migrate
show_success "Migraciones completadas"

# Crear superusuario si no existe
show_message "Verificando superusuario..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@felicita.pe', 'admin123')" | python manage.py shell
show_success "Superusuario verificado (admin/admin123)"

# Cargar datos iniciales
show_message "Cargando datos iniciales..."
if [ -f "fixtures/datos_iniciales.json" ]; then
    python manage.py loaddata fixtures/datos_iniciales.json
    show_success "Datos iniciales cargados"
fi

# Recolectar archivos estáticos
show_message "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput
show_success "Archivos estáticos recolectados"

# Volver al directorio raíz
cd ..

# Configurar Frontend
show_message "Configurando Frontend React..."
cd frontend

# Instalar dependencias Node.js
show_message "Instalando dependencias Node.js..."
npm install
show_success "Dependencias Node.js instaladas"

# Volver al directorio raíz
cd ..

# Mostrar URLs importantes
echo -e "\n${GREEN}🎉 ¡FELICITA está listo para desarrollo!${NC}\n"

echo -e "${CYAN}📍 URLs importantes:${NC}"
echo -e "   🌐 Frontend React:     ${YELLOW}http://localhost:3000${NC}"
echo -e "   🔧 Backend Django:     ${YELLOW}http://localhost:8000${NC}"
echo -e "   📊 Admin Django:       ${YELLOW}http://localhost:8000/admin/${NC}"
echo -e "   🗄️  phpMyAdmin:        ${YELLOW}http://localhost:8080${NC}"
echo -e "   📱 API Docs:           ${YELLOW}http://localhost:8000/api/docs/${NC}"

echo -e "\n${CYAN}🔑 Credenciales por defecto:${NC}"
echo -e "   👤 Admin Django:       ${YELLOW}admin / admin123${NC}"
echo -e "   🗄️  MySQL Root:        ${YELLOW}root / root_password_123${NC}"
echo -e "   🗄️  MySQL Usuario:     ${YELLOW}felicita_user / dev_password_123${NC}"

echo -e "\n${CYAN}🚀 Para iniciar los servidores:${NC}"
echo -e "   📘 Backend:  ${YELLOW}cd backend && source venv/bin/activate && python manage.py runserver${NC}"
echo -e "   📗 Frontend: ${YELLOW}cd frontend && npm run dev${NC}"

echo -e "\n${CYAN}🛠️  Comandos útiles:${NC}"
echo -e "   🔄 Reiniciar DB:       ${YELLOW}docker-compose restart db${NC}"
echo -e "   📋 Ver logs:           ${YELLOW}docker-compose logs -f${NC}"
echo -e "   🛑 Parar todo:         ${YELLOW}docker-compose down${NC}"
echo -e "   🧹 Limpiar volúmenes:  ${YELLOW}docker-compose down -v${NC}"

echo -e "\n${PURPLE}¡Desarrollo con FELICITA iniciado exitosamente! 🇵🇪${NC}\n"

# Preguntar si quiere iniciar los servidores automáticamente
read -p "¿Deseas iniciar los servidores automáticamente? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    show_message "Iniciando servidores..."
    
    # Abrir terminales para backend y frontend
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --tab --title="FELICITA Backend" -- bash -c "cd backend && source venv/bin/activate && python manage.py runserver; exec bash"
        gnome-terminal --tab --title="FELICITA Frontend" -- bash -c "cd frontend && npm run dev; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -title "FELICITA Backend" -e "cd backend && source venv/bin/activate && python manage.py runserver" &
        xterm -title "FELICITA Frontend" -e "cd frontend && npm run dev" &
    else
        show_warning "No se pudo abrir terminales automáticamente. Ejecuta manualmente:"
        echo "Terminal 1: cd backend && source venv/bin/activate && python manage.py runserver"
        echo "Terminal 2: cd frontend && npm run dev"
    fi
fi