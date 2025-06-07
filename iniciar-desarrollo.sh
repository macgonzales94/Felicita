#!/bin/bash

# =============================================================================
# SCRIPT DE INICIALIZACIÓN - PROYECTO FELICITA
# Sistema de Facturación Electrónica para Perú
# =============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para mostrar encabezado
show_header() {
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "🚀 FELICITA - SISTEMA DE FACTURACIÓN ELECTRÓNICA PARA PERÚ"
    echo "============================================================================="
    echo -e "${NC}"
}

# Función para mostrar mensaje de éxito
show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar mensaje de error
show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para mostrar mensaje de información
show_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Función para mostrar mensaje de advertencia
show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        show_error "Docker no está instalado. Por favor instala Docker primero."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        show_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
        exit 1
    fi
    
    show_success "Docker y Docker Compose están instalados"
}

# Verificar si Python está instalado
check_python() {
    if ! command -v python3 &> /dev/null; then
        show_error "Python 3 no está instalado. Por favor instala Python 3.8 o superior."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    show_success "Python $PYTHON_VERSION encontrado"
}

# Verificar si Node.js está instalado
check_node() {
    if ! command -v node &> /dev/null; then
        show_error "Node.js no está instalado. Por favor instala Node.js 16 o superior."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        show_error "npm no está instalado. Por favor instala npm."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    show_success "Node.js $NODE_VERSION y npm $NPM_VERSION encontrados"
}

# Crear archivos de configuración si no existen
setup_env_files() {
    show_info "Configurando archivos de entorno..."
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cp .env.example backend/.env
        show_success "Archivo backend/.env creado desde .env.example"
    else
        show_info "Archivo backend/.env ya existe"
    fi
    
    # Frontend .env
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
# FRONTEND DEVELOPMENT - FELICITA
VITE_APP_NAME=FELICITA
VITE_APP_VERSION=1.0.0
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
VITE_ENVIRONMENT=development
EOF
        show_success "Archivo frontend/.env creado"
    else
        show_info "Archivo frontend/.env ya existe"
    fi
}

# Instalar dependencias del backend
setup_backend() {
    show_info "Configurando backend Django..."
    
    cd backend
    
    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        show_success "Entorno virtual creado"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Instalar dependencias
    pip install --upgrade pip
    pip install -r requirements.txt
    show_success "Dependencias del backend instaladas"
    
    cd ..
}

# Instalar dependencias del frontend
setup_frontend() {
    show_info "Configurando frontend React..."
    
    cd frontend
    
    # Instalar dependencias
    npm install
    show_success "Dependencias del frontend instaladas"
    
    cd ..
}

# Iniciar servicios con Docker
start_docker_services() {
    show_info "Iniciando servicios Docker..."
    
    # Detener contenedores existentes
    docker-compose down
    
    # Construir e iniciar contenedores
    docker-compose up -d db_felicita redis_felicita adminer_felicita
    
    # Esperar a que los servicios estén listos
    show_info "Esperando a que PostgreSQL esté listo..."
    sleep 10
    
    # Verificar que PostgreSQL esté funcionando
    until docker-compose exec db_felicita pg_isready -U felicita_user -d felicita_db; do
        show_info "Esperando a PostgreSQL..."
        sleep 2
    done
    
    show_success "Servicios Docker iniciados correctamente"
}

# Configurar base de datos
setup_database() {
    show_info "Configurando base de datos..."
    
    cd backend
    source venv/bin/activate
    
    # Aplicar migraciones
    python manage.py makemigrations
    python manage.py migrate
    show_success "Migraciones aplicadas"
    
    # Cargar datos iniciales
    if [ -f "fixtures/datos_iniciales.json" ]; then
        python manage.py loaddata fixtures/datos_iniciales.json
        show_success "Datos iniciales cargados"
    fi
    
    # Crear superusuario si no existe
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@felicita.pe').exists() or User.objects.create_superuser('admin@felicita.pe', 'admin123', nombres='Administrador', apellido_paterno='Sistema', apellido_materno='FELICITA', numero_documento='12345678')" | python manage.py shell
    show_success "Superusuario creado (admin@felicita.pe / admin123)"
    
    cd ..
}

# Mostrar información de URLs
show_urls() {
    echo -e "${PURPLE}"
    echo "============================================================================="
    echo "🌐 URLs DEL SISTEMA FELICITA"
    echo "============================================================================="
    echo -e "${NC}"
    echo -e "${GREEN}📱 Frontend (React):${NC}        http://localhost:3000"
    echo -e "${GREEN}🔧 Backend API (Django):${NC}    http://localhost:8000"
    echo -e "${GREEN}📋 Admin Django:${NC}            http://localhost:8000/admin"
    echo -e "${GREEN}📖 API Docs:${NC}                http://localhost:8000/docs"
    echo -e "${GREEN}🗄️  Adminer (DB):${NC}            http://localhost:8080"
    echo -e "${GREEN}📊 Health Check:${NC}            http://localhost:8000/health"
    echo ""
    echo -e "${YELLOW}👤 Credenciales Admin:${NC}"
    echo -e "   Email: admin@felicita.pe"
    echo -e "   Password: admin123"
    echo ""
    echo -e "${YELLOW}🗄️  Base de Datos:${NC}"
    echo -e "   Host: localhost"
    echo -e "   Puerto: 5432"
    echo -e "   DB: felicita_db"
    echo -e "   Usuario: felicita_user"
    echo -e "   Password: felicita_2024_dev"
}

# Función principal
main() {
    show_header
    
    show_info "Verificando requisitos del sistema..."
    check_docker
    check_python
    check_node
    
    show_info "Configurando entorno de desarrollo..."
    setup_env_files
    
    show_info "Instalando dependencias..."
    setup_backend
    setup_frontend
    
    show_info "Iniciando servicios..."
    start_docker_services
    setup_database
    
    show_success "¡FELICITA configurado correctamente!"
    show_urls
    
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "🚀 COMANDOS PARA INICIAR DESARROLLO:"
    echo "============================================================================="
    echo -e "${NC}"
    echo -e "${GREEN}Backend (Terminal 1):${NC}"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   python manage.py runserver"
    echo ""
    echo -e "${GREEN}Frontend (Terminal 2):${NC}"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
    echo -e "${GREEN}Ver logs de Docker:${NC}"
    echo "   docker-compose logs -f"
    echo ""
    echo -e "${GREEN}Detener servicios:${NC}"
    echo "   docker-compose down"
    echo ""
}

# Ejecutar función principal
main "$@"