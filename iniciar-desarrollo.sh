#!/bin/bash

# =============================================================================
# SCRIPT DE INICIALIZACIÓN ACTUALIZADO - PROYECTO FELICITA
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

# Variables de configuración
COMPOSE_FILE="docker-compose.dev.yml"
PROJECT_NAME="felicita"

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

# Función para mostrar progreso
show_progress() {
    echo -e "${PURPLE}⏳ $1${NC}"
}

# Verificar si Docker está instalado y funcionando
check_docker() {
    show_info "Verificando Docker..."
    
    if ! command -v docker &> /dev/null; then
        show_error "Docker no está instalado. Por favor instala Docker primero."
        echo "Visita: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        show_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
        echo "Visita: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Verificar que Docker esté corriendo
    if ! docker info &> /dev/null; then
        show_error "Docker no está corriendo. Por favor inicia Docker primero."
        exit 1
    fi
    
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    
    show_success "Docker $DOCKER_VERSION y Docker Compose $COMPOSE_VERSION están listos"
}

# Verificar archivos requeridos del proyecto
check_project_files() {
    show_info "Verificando estructura del proyecto..."
    
    REQUIRED_FILES=(
        "$COMPOSE_FILE"
        ".env.example"
        "backend/Dockerfile"
        "frontend/Dockerfile"
        "backend/requirements.txt"
        "frontend/package.json"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            show_error "Archivo requerido no encontrado: $file"
            show_info "Asegúrate de estar en el directorio raíz del proyecto FELICITA"
            exit 1
        fi
    done
    
    show_success "Estructura del proyecto verificada"
}

# Crear archivos de configuración si no existen
setup_env_files() {
    show_info "Configurando archivos de entorno..."
    
    # Archivo .env principal
    if [ ! -f ".env" ]; then
        cp .env.example .env
        show_success "Archivo .env creado desde .env.example"
    else
        show_info "Archivo .env ya existe"
    fi
    
    # Backend .env (si existe directorio backend separado)
    if [ -d "backend" ] && [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
# BACKEND DEVELOPMENT - FELICITA
DJANGO_SETTINGS_MODULE=config.settings.local
DEBUG=True
SECRET_KEY=dev-secret-key-felicita-2024-not-for-production
EOF
        show_success "Archivo backend/.env creado"
    fi
    
    # Frontend .env
    if [ -d "frontend" ] && [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
# FRONTEND DEVELOPMENT - FELICITA
VITE_APP_NAME=FELICITA
VITE_APP_VERSION=1.0.0
VITE_API_URL=http://localhost:8000
VITE_APP_DESCRIPTION=Sistema de Facturación Electrónica para Perú
VITE_ENVIRONMENT=development
EOF
        show_success "Archivo frontend/.env creado"
    else
        show_info "Archivo frontend/.env ya existe"
    fi
}

# Limpiar contenedores y volúmenes anteriores si existen
cleanup_previous() {
    show_info "Limpiando instalación anterior (si existe)..."
    
    # Detener contenedores
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    
    # Limpiar contenedores huérfanos del script anterior
    docker-compose down --remove-orphans 2>/dev/null || true
    
    show_success "Limpieza completada"
}

# Construir imágenes Docker
build_images() {
    show_progress "Construyendo imágenes Docker..."
    
    if ! docker-compose -f "$COMPOSE_FILE" build; then
        show_error "Error al construir las imágenes Docker"
        exit 1
    fi
    
    show_success "Imágenes Docker construidas correctamente"
}

# Iniciar servicios base (DB, Redis)
start_base_services() {
    show_progress "Iniciando servicios base (PostgreSQL, Redis)..."
    
    docker-compose -f "$COMPOSE_FILE" up -d db redis
    
    # Esperar a que PostgreSQL esté listo
    show_info "Esperando a que PostgreSQL esté listo..."
    timeout=60
    counter=0
    
    while ! docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U felicita_user -d felicita_dev &>/dev/null; do
        if [ $counter -ge $timeout ]; then
            show_error "Timeout: PostgreSQL no está respondiendo después de $timeout segundos"
            exit 1
        fi
        show_info "PostgreSQL aún no está listo... ($counter/$timeout)"
        sleep 2
        ((counter+=2))
    done
    
    # Esperar a que Redis esté listo
    show_info "Verificando Redis..."
    if ! docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping &>/dev/null; then
        show_warning "Redis podría no estar completamente listo, pero continuando..."
    fi
    
    show_success "Servicios base iniciados y listos"
}

# Configurar base de datos
setup_database() {
    show_progress "Configurando base de datos..."
    
    # Aplicar migraciones
    show_info "Aplicando migraciones de Django..."
    if ! docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate; then
        show_error "Error al aplicar migraciones"
        exit 1
    fi
    
    # Crear superusuario si no existe
    show_info "Creando superusuario admin..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py shell << EOF
from aplicaciones.usuarios.models import Usuario
if not Usuario.objects.filter(email='admin@felicita.pe').exists():
    Usuario.objects.create_superuser(
        email='admin@felicita.pe',
        password='admin123',
        nombres='Administrador',
        apellido_paterno='Sistema',
        apellido_materno='FELICITA',
        numero_documento='12345678',
        tipo_documento='DNI'
    )
    print('Superusuario creado')
else:
    print('Superusuario ya existe')
EOF
    
    # Cargar datos iniciales si existen
    if [ -f "backend/fixtures/datos_iniciales.json" ]; then
        show_info "Cargando datos iniciales..."
        docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py loaddata fixtures/datos_iniciales.json
        show_success "Datos iniciales cargados"
    fi
    
    show_success "Base de datos configurada correctamente"
}

# Iniciar todos los servicios
start_all_services() {
    show_progress "Iniciando todos los servicios..."
    
    if ! docker-compose -f "$COMPOSE_FILE" up -d; then
        show_error "Error al iniciar los servicios"
        exit 1
    fi
    
    # Esperar a que los servicios estén listos
    show_info "Esperando a que todos los servicios estén listos..."
    sleep 10
    
    # Verificar salud de los servicios
    show_info "Verificando estado de los servicios..."
    
    # Backend health check
    timeout=30
    counter=0
    while ! curl -s http://localhost:8000/api/health/ &>/dev/null; do
        if [ $counter -ge $timeout ]; then
            show_warning "Backend tardó más de lo esperado en estar listo"
            break
        fi
        sleep 2
        ((counter+=2))
    done
    
    # Frontend health check
    timeout=30
    counter=0
    while ! curl -s http://localhost:5173/ &>/dev/null; do
        if [ $counter -ge $timeout ]; then
            show_warning "Frontend tardó más de lo esperado en estar listo"
            break
        fi
        sleep 2
        ((counter+=2))
    done
    
    show_success "Todos los servicios iniciados"
}

# Mostrar estado de los servicios
show_services_status() {
    show_info "Estado de los servicios:"
    docker-compose -f "$COMPOSE_FILE" ps
}

# Mostrar información de URLs y credenciales
show_urls() {
    echo ""
    echo -e "${PURPLE}"
    echo "============================================================================="
    echo "🌐 URLs DEL SISTEMA FELICITA"
    echo "============================================================================="
    echo -e "${NC}"
    echo -e "${GREEN}📱 Frontend (React + Vite):${NC}   http://localhost:5173"
    echo -e "${GREEN}🔧 Backend API (Django):${NC}     http://localhost:8000/api"
    echo -e "${GREEN}📋 Admin Django:${NC}             http://localhost:8000/admin"
    echo -e "${GREEN}📖 API Documentation:${NC}        http://localhost:8000/api/docs"
    echo -e "${GREEN}🗄️  PgAdmin (Database):${NC}       http://localhost:5050"
    echo -e "${GREEN}📧 MailHog (Email Dev):${NC}       http://localhost:8025"
    echo -e "${GREEN}🌸 Flower (Celery Monitor):${NC}  http://localhost:5555"
    echo -e "${GREEN}🔍 Health Check:${NC}             http://localhost:8000/api/health/"
    echo ""
    echo -e "${YELLOW}👤 CREDENCIALES:${NC}"
    echo -e "${CYAN}Django Admin:${NC}"
    echo -e "   📧 Email: admin@felicita.pe"
    echo -e "   🔑 Password: admin123"
    echo ""
    echo -e "${CYAN}PgAdmin:${NC}"
    echo -e "   📧 Email: admin@felicita.dev"
    echo -e "   🔑 Password: admin123"
    echo ""
    echo -e "${CYAN}Flower:${NC}"
    echo -e "   👤 Usuario: admin"
    echo -e "   🔑 Password: flower123"
    echo ""
    echo -e "${CYAN}Base de Datos:${NC}"
    echo -e "   🏠 Host: localhost:5432"
    echo -e "   🗃️  Database: felicita_dev"
    echo -e "   👤 Usuario: felicita_user"
    echo -e "   🔑 Password: felicita_password_dev_2024"
}

# Mostrar comandos útiles
show_useful_commands() {
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "🛠️  COMANDOS ÚTILES"
    echo "============================================================================="
    echo -e "${NC}"
    echo -e "${GREEN}Ver logs de todos los servicios:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE logs -f"
    echo ""
    echo -e "${GREEN}Ver logs de un servicio específico:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE logs -f backend"
    echo "   docker-compose -f $COMPOSE_FILE logs -f frontend"
    echo ""
    echo -e "${GREEN}Ejecutar comandos en el backend:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE exec backend python manage.py shell"
    echo "   docker-compose -f $COMPOSE_FILE exec backend python manage.py createsuperuser"
    echo ""
    echo -e "${GREEN}Reiniciar un servicio:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE restart backend"
    echo ""
    echo -e "${GREEN}Detener todos los servicios:${NC}"
    echo "   docker-compose -f $COMPOSE_FILE down"
    echo ""
    echo -e "${GREEN}Limpiar todo (incluyendo volúmenes):${NC}"
    echo "   docker-compose -f $COMPOSE_FILE down -v"
    echo ""
}

# Función principal
main() {
    show_header
    
    # Verificaciones
    check_docker
    check_project_files
    
    # Configuración
    setup_env_files
    
    # Limpieza
    cleanup_previous
    
    # Construcción e inicio
    build_images
    start_base_services
    setup_database
    start_all_services
    
    # Información final
    show_services_status
    show_success "¡FELICITA configurado e iniciado correctamente!"
    show_urls
    show_useful_commands
    
    echo -e "${GREEN}"
    echo "============================================================================="
    echo "🎉 ¡FELICITA ESTÁ LISTO PARA USAR!"
    echo "============================================================================="
    echo -e "${NC}"
    echo -e "${YELLOW}Presiona Ctrl+C para detener los servicios cuando termines${NC}"
    echo ""
    
    # Opcional: seguir logs en tiempo real
    read -p "¿Quieres ver los logs en tiempo real? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# Manejo de señales para limpieza
cleanup_on_exit() {
    echo ""
    show_info "Deteniendo servicios..."
    docker-compose -f "$COMPOSE_FILE" down
    show_success "Servicios detenidos correctamente"
    exit 0
}

trap cleanup_on_exit SIGINT SIGTERM

# Ejecutar función principal
main "$@"