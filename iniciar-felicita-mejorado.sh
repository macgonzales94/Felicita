#!/bin/bash

# =============================================================================
# SCRIPT DE INICIALIZACIÓN MEJORADO - PROYECTO FELICITA
# Sistema de Facturación Electrónica para Perú
# Versión: 2.0 - Re-ejecutable y robusto
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
SCRIPT_VERSION="2.0"

# Función para mostrar encabezado
show_header() {
    clear
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "🚀 FELICITA - SISTEMA DE FACTURACIÓN ELECTRÓNICA PARA PERÚ"
    echo "    Versión del Script: $SCRIPT_VERSION"
    echo "============================================================================="
    echo -e "${NC}"
}

# Funciones de mensajes (mantener las existentes)
show_success() { echo -e "${GREEN}✅ $1${NC}"; }
show_error() { echo -e "${RED}❌ $1${NC}"; }
show_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
show_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
show_progress() { echo -e "${PURPLE}⏳ $1${NC}"; }

# Función para detectar si los servicios ya están corriendo
check_running_services() {
    show_info "Verificando servicios existentes..."
    
    RUNNING_CONTAINERS=$(docker-compose -f "$COMPOSE_FILE" ps --services --filter "status=running" 2>/dev/null | wc -l)
    
    if [ "$RUNNING_CONTAINERS" -gt 0 ]; then
        echo -e "${YELLOW}"
        echo "⚠️  SERVICIOS FELICITA YA ESTÁN CORRIENDO"
        echo "============================================================================="
        echo -e "${NC}"
        docker-compose -f "$COMPOSE_FILE" ps
        echo ""
        echo -e "${CYAN}¿Qué quieres hacer?${NC}"
        echo -e "${GREEN}1)${NC} Reiniciar todos los servicios (recomendado)"
        echo -e "${GREEN}2)${NC} Detener y limpiar todo, luego iniciar desde cero"
        echo -e "${GREEN}3)${NC} Solo verificar estado y mostrar URLs"
        echo -e "${GREEN}4)${NC} Salir sin cambios"
        echo ""
        read -p "Selecciona una opción (1-4): " -n 1 -r
        echo ""
        
        case $REPLY in
            1)
                show_info "Reiniciando servicios existentes..."
                restart_services
                return 0
                ;;
            2)
                show_info "Limpiando todo y reiniciando desde cero..."
                cleanup_everything
                return 1  # Continúa con setup completo
                ;;
            3)
                show_status_and_exit
                return 0
                ;;
            4)
                show_info "Saliendo sin cambios..."
                exit 0
                ;;
            *)
                show_warning "Opción inválida, reiniciando servicios..."
                restart_services
                return 0
                ;;
        esac
    fi
    
    return 1  # No hay servicios corriendo, continuar con setup completo
}

# Función para reiniciar servicios existentes
restart_services() {
    show_progress "Reiniciando servicios FELICITA..."
    
    # Reiniciar en orden específico
    docker-compose -f "$COMPOSE_FILE" restart db redis
    sleep 5
    docker-compose -f "$COMPOSE_FILE" restart backend
    sleep 10
    docker-compose -f "$COMPOSE_FILE" restart frontend
    sleep 5
    
    # Verificar que todo esté funcionando
    verify_services_health
    show_final_info
}

# Función para limpiar todo
cleanup_everything() {
    show_warning "Deteniendo y limpiando todos los servicios..."
    
    # Detener todos los contenedores
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Preguntar si limpiar volúmenes
    echo -e "${YELLOW}¿Quieres limpiar también la base de datos? (se perderán todos los datos)${NC}"
    read -p "Limpiar BD (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" down -v
        show_warning "Base de datos limpiada - se crearán datos nuevos"
    fi
    
    # Limpiar imágenes huérfanas
    docker image prune -f >/dev/null 2>&1
    
    show_success "Limpieza completada"
}

# Función para mostrar estado y salir
show_status_and_exit() {
    show_info "Estado actual de los servicios:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    verify_services_health
    show_final_info
    exit 0
}

# Verificar que Docker esté funcionando (mejorado)
check_docker() {
    show_info "Verificando Docker..."
    
    if ! command -v docker &> /dev/null; then
        show_error "Docker no está instalado."
        echo "Instala Docker desde: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        show_error "Docker Compose no está instalado."
        echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        show_error "Docker no está corriendo. Iniciando Docker..."
        # Intentar iniciar Docker (funciona en algunas distribuciones)
        sudo systemctl start docker 2>/dev/null || true
        sleep 3
        
        if ! docker info &> /dev/null; then
            show_error "No se pudo iniciar Docker. Por favor, inicia Docker manualmente."
            exit 1
        fi
    fi
    
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    
    show_success "Docker $DOCKER_VERSION y Docker Compose $COMPOSE_VERSION listos"
}

# Verificar puertos libres (nuevo)
check_ports() {
    show_info "Verificando puertos requeridos..."
    
    REQUIRED_PORTS=(5173 8000 5432 6379 5050 8025 5555)
    CONFLICTING_PORTS=()
    
    for port in "${REQUIRED_PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            # Verificar si es nuestro Docker Compose
            if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q ":$port->"; then
                CONFLICTING_PORTS+=($port)
            fi
        fi
    done
    
    if [ ${#CONFLICTING_PORTS[@]} -gt 0 ]; then
        show_warning "Puertos en uso por otros procesos: ${CONFLICTING_PORTS[*]}"
        echo "Esto podría causar conflictos. ¿Continuar de todas formas? (y/n)"
        read -p "Continuar: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    show_success "Puertos verificados"
}

# Verificar archivos del proyecto (mejorado)
check_project_files() {
    show_info "Verificando estructura del proyecto..."
    
    REQUIRED_FILES=(
        "$COMPOSE_FILE"
        "backend/Dockerfile"
        "frontend/Dockerfile"
        "backend/requirements.txt"
        "frontend/package.json"
    )
    
    MISSING_FILES=()
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            MISSING_FILES+=("$file")
        fi
    done
    
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        show_error "Archivos faltantes:"
        for file in "${MISSING_FILES[@]}"; do
            echo "   - $file"
        done
        show_info "Asegúrate de estar en el directorio raíz del proyecto FELICITA"
        exit 1
    fi
    
    show_success "Estructura del proyecto verificada"
}

# Configurar archivos de entorno (mejorado)
setup_env_files() {
    show_info "Configurando archivos de entorno..."
    
    # Backup de archivos existentes si existen
    if [ -f ".env" ]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
        show_info "Backup de .env creado"
    fi
    
    # Crear .env principal si no existe
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            show_success "Archivo .env creado desde .env.example"
        else
            create_default_env
        fi
    else
        show_info "Archivo .env ya existe (backup creado)"
    fi
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
DJANGO_SETTINGS_MODULE=config.settings.local
DEBUG=True
SECRET_KEY=dev-secret-key-felicita-2024-not-for-production-$(date +%s)
EOF
        show_success "Archivo backend/.env creado"
    fi
    
    # Frontend .env
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
VITE_APP_NAME=FELICITA
VITE_APP_VERSION=1.0.0
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
EOF
        show_success "Archivo frontend/.env creado"
    fi
}

# Crear archivo .env por defecto
create_default_env() {
    cat > .env << EOF
# FELICITA - Configuración de desarrollo
COMPOSE_PROJECT_NAME=felicita
ENVIRONMENT=development

# PostgreSQL
POSTGRES_DB=felicita_dev
POSTGRES_USER=felicita_user
POSTGRES_PASSWORD=felicita_password_dev_2024

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@felicita.dev
PGADMIN_DEFAULT_PASSWORD=admin123

# Redis
REDIS_PASSWORD=

# MailHog
MAILHOG_WEB_PORT=8025
MAILHOG_SMTP_PORT=1025

# Flower
FLOWER_USER=admin
FLOWER_PASSWORD=flower123
EOF
    show_success "Archivo .env por defecto creado"
}

# Construir imágenes con cache inteligente
build_images() {
    show_progress "Construyendo imágenes Docker..."
    
    # Verificar si las imágenes necesitan reconstruirse
    if docker-compose -f "$COMPOSE_FILE" images | grep -q "felicita"; then
        echo -e "${YELLOW}Imágenes existentes encontradas. ¿Forzar reconstrucción?${NC}"
        echo "1) No, usar imágenes existentes (más rápido)"
        echo "2) Sí, reconstruir todo (recomendado si hay cambios)"
        read -p "Selecciona (1-2): " -n 1 -r
        echo ""
        
        if [[ $REPLY == "2" ]]; then
            docker-compose -f "$COMPOSE_FILE" build --no-cache
        fi
    else
        docker-compose -f "$COMPOSE_FILE" build
    fi
    
    show_success "Imágenes Docker listas"
}

# Iniciar servicios base con mejor espera
start_base_services() {
    show_progress "Iniciando servicios base (PostgreSQL, Redis)..."
    
    docker-compose -f "$COMPOSE_FILE" up -d db redis
    
    # Esperar PostgreSQL con timeout mejorado
    show_info "Esperando PostgreSQL..."
    timeout=90
    counter=0
    
    while ! docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U felicita_user &>/dev/null; do
        if [ $counter -ge $timeout ]; then
            show_error "PostgreSQL no responde después de $timeout segundos"
            show_info "Verificando logs de PostgreSQL..."
            docker-compose -f "$COMPOSE_FILE" logs db | tail -20
            exit 1
        fi
        
        if [ $((counter % 10)) -eq 0 ]; then
            show_info "PostgreSQL iniciando... ($counter/$timeout segundos)"
        fi
        
        sleep 2
        ((counter+=2))
    done
    
    # Verificar Redis
    show_info "Verificando Redis..."
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
        show_success "Redis funcionando correctamente"
    else
        show_warning "Redis podría tener problemas, pero continuando..."
    fi
    
    show_success "Servicios base listos"
}

# Configurar base de datos con mejor manejo de errores
# =============================================================================
# CORRECCIÓN PARA EL SCRIPT - GESTIÓN DE DATOS INICIALES
# =============================================================================

# En lugar de crear empresa y luego cargar fixtures...
# PRIMERO: Verificar si existen fixtures
# SEGUNDO: Cargar fixtures O crear datos manualmente

# REEMPLAZAR LA SECCIÓN DE setup_database() con esto:

setup_database() {
    show_progress "Configurando base de datos..."
    
    # Iniciar backend
    docker-compose -f "$COMPOSE_FILE" up -d backend
    
    # Esperar backend
    show_info "Esperando que el backend Django esté listo..."
    timeout=120
    counter=0
    
    while ! docker-compose -f "$COMPOSE_FILE" exec -T backend python -c "import django; django.setup()" &>/dev/null; do
        if [ $counter -ge $timeout ]; then
            show_error "Backend no está listo después de $timeout segundos"
            exit 1
        fi
        
        if [ $((counter % 15)) -eq 0 ]; then
            show_info "Backend iniciando... ($counter/$timeout segundos)"
        fi
        
        sleep 3
        ((counter+=3))
    done
    
    # Aplicar migraciones
    show_info "Aplicando migraciones..."
    if ! docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate; then
        show_error "Error al aplicar migraciones"
        exit 1
    fi
    
    # NUEVO: Verificar si cargar fixtures o crear datos manualmente
    if [ -f "backend/fixtures/datos_iniciales.json" ]; then
        show_info "Cargando fixtures (datos iniciales)..."
        if docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py loaddata fixtures/datos_iniciales.json; then
            show_success "Fixtures cargados correctamente"
        else
            show_warning "Error al cargar fixtures, creando datos manualmente..."
            create_manual_data
        fi
    else
        show_info "No hay fixtures, creando datos iniciales manualmente..."
        create_manual_data
    fi
    
    show_success "Base de datos configurada correctamente"
}

# NUEVA FUNCIÓN: Crear datos manualmente solo si no existen
create_manual_data() {
    docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py shell << 'EOF'
try:
    from aplicaciones.core.models import Empresa
    from aplicaciones.usuarios.models import Usuario
    
    # Solo crear empresa si NO existe
    empresa, created = Empresa.objects.get_or_create(
        ruc="20123456789",
        defaults={
            "razon_social": "EMPRESA DEMO FELICITA S.A.C.",
            "nombre_comercial": "FELICITA DEMO",
            "direccion": "AV. DEMO 123, SAN ISIDRO, LIMA",
            "distrito": "San Isidro",
            "provincia": "Lima", 
            "departamento": "Lima",
            "ubigeo": "150101",
            "telefono": "01-2345678",
            "email": "contacto@demo-felicita.pe",
            "activo": True
        }
    )
    
    if created:
        print("✅ Empresa demo creada")
    else:
        print("✅ Empresa demo ya existe")
    
    # Solo crear usuarios si NO existen
    usuarios_demo = [
        {
            'email': 'admin@felicita.pe',
            'username': 'admin',
            'password': 'admin123',
            'nombres': 'Administrador',
            'apellido_paterno': 'Sistema',
            'apellido_materno': 'FELICITA',
            'numero_documento': '12345678',
            'is_superuser': True,
            'is_staff': True
        },
        {
            'email': 'contador@felicita.pe',
            'username': 'contador', 
            'password': 'contador123',
            'nombres': 'Juan Carlos',
            'apellido_paterno': 'Contador',
            'apellido_materno': 'Pérez',
            'numero_documento': '87654321',
            'cargo': 'Contador Principal'
        },
        {
            'email': 'vendedor@felicita.pe',
            'username': 'vendedor',
            'password': 'vendedor123',
            'nombres': 'María',
            'apellido_paterno': 'Vendedora', 
            'apellido_materno': 'García',
            'numero_documento': '11223344',
            'cargo': 'Vendedor POS'
        }
    ]
    
    for user_data in usuarios_demo:
        email = user_data['email']
        if not Usuario.objects.filter(email=email).exists():
            user_data['tipo_documento'] = 'DNI'
            user_data['empresa'] = empresa
            
            # Crear superuser o user normal
            if user_data.pop('is_superuser', False):
                Usuario.objects.create_superuser(**user_data)
            else:
                Usuario.objects.create_user(**user_data)
                
            print(f"✅ Usuario {email} creado")
        else:
            print(f"✅ Usuario {email} ya existe")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF
}

# DESPUÉS viene la lógica de setup_database
setup_database() {
    show_progress "Configurando base de datos..."
    
    # ... migraciones ...
    
    # NUEVO: Verificar si cargar fixtures o crear datos manualmente
    if [ -f "backend/fixtures/datos_iniciales.json" ]; then
        show_info "Cargando fixtures (datos iniciales)..."
        if docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py loaddata fixtures/datos_iniciales.json; then
            show_success "Fixtures cargados correctamente"
        else
            show_warning "Error al cargar fixtures, creando datos manualmente..."
            create_manual_data
        fi
    else
        show_info "No hay fixtures, creando datos iniciales manualmente..."
        create_manual_data
    fi
    
    show_success "Base de datos configurada correctamente"
}

# Verificar salud de servicios
verify_services_health() {
    show_info "Verificando salud de los servicios..."
    
    # Health checks
    services_status=()
    
    # Backend
    if curl -s -f http://localhost:8000/health/ >/dev/null 2>&1; then
        services_status+=("✅ Backend API")
    else
        services_status+=("❌ Backend API")
    fi
    
    # Frontend
    if curl -s -f http://localhost:5173/ >/dev/null 2>&1; then
        services_status+=("✅ Frontend React")
    else
        services_status+=("❌ Frontend React")
    fi
    
    # PostgreSQL
    if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready >/dev/null 2>&1; then
        services_status+=("✅ PostgreSQL")
    else
        services_status+=("❌ PostgreSQL")
    fi
    
    # Redis
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
        services_status+=("✅ Redis")
    else
        services_status+=("❌ Redis")
    fi
    
    echo ""
    show_info "Estado de servicios:"
    for status in "${services_status[@]}"; do
        echo "   $status"
    done
    echo ""
}

# Mostrar información final mejorada
show_final_info() {
    echo ""
    echo -e "${PURPLE}"
    echo "============================================================================="
    echo "🌐 SISTEMA FELICITA DISPONIBLE EN:"
    echo "============================================================================="
    echo -e "${NC}"
    
    # URLs principales
    echo -e "${GREEN}🖥️  Aplicación Principal:${NC}    http://localhost:5173"
    echo -e "${GREEN}🔧 API Backend:${NC}             http://localhost:8000/api"
    echo -e "${GREEN}📋 Panel Admin:${NC}             http://localhost:8000/admin"
    echo -e "${GREEN}📖 Documentación API:${NC}       http://localhost:8000/docs"
    echo ""
    
    # URLs adicionales  
    echo -e "${CYAN}🛠️  Herramientas de Desarrollo:${NC}"
    echo -e "   🗄️  PgAdmin:                  http://localhost:5050"
    echo -e "   📧 MailHog:                   http://localhost:8025"
    echo -e "   🌸 Flower (Celery):           http://localhost:5555"
    echo -e "   🔍 Health Check:              http://localhost:8000/health/"
    echo ""
    
    # Credenciales
    echo -e "${YELLOW}🔑 CREDENCIALES:${NC}"
    echo -e "${GREEN}Aplicación FELICITA:${NC}"
    echo -e "   📧 admin@felicita.pe / admin123 (Administrador)"
    echo -e "   📧 contador@felicita.pe / contador123 (Contador)"  
    echo -e "   📧 vendedor@felicita.pe / vendedor123 (Vendedor)"
    echo ""
    echo -e "${GREEN}PgAdmin:${NC} admin@felicita.dev / admin123"
    echo -e "${GREEN}Flower:${NC} admin / flower123"
    echo ""
    
    # Comandos útiles
    echo -e "${CYAN}🛠️  COMANDOS ÚTILES:${NC}"
    echo -e "   Ver logs:          docker-compose -f $COMPOSE_FILE logs -f"
    echo -e "   Reiniciar:         docker-compose -f $COMPOSE_FILE restart"
    echo -e "   Detener:           docker-compose -f $COMPOSE_FILE down"
    echo -e "   Estado:            docker-compose -f $COMPOSE_FILE ps"
    echo ""
}

# Función principal mejorada
main() {
    show_header
    
    # Verificaciones básicas
    check_docker
    check_project_files
    check_ports
    
    # Verificar si ya está corriendo
    if check_running_services; then
        # Ya se manejó en check_running_services
        exit 0
    fi
    
    # Setup completo
    setup_env_files
    build_images
    start_base_services
    setup_database
    
    # Iniciar todos los servicios
    show_progress "Iniciando todos los servicios..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Esperar un momento para que se estabilicen
    sleep 15
    
    # Verificar salud
    verify_services_health
    
    # Mostrar información final
    show_success "¡FELICITA configurado e iniciado correctamente!"
    show_final_info
    
    echo -e "${GREEN}"
    echo "============================================================================="
    echo "🎉 ¡FELICITA ESTÁ LISTO! Ve a http://localhost:5173"
    echo "============================================================================="
    echo -e "${NC}"
}

# Manejo de señales para limpieza
cleanup_on_exit() {
    echo ""
    show_info "Señal de interrupción recibida..."
    echo -e "${YELLOW}¿Quieres detener los servicios? (y/n)${NC}"
    read -p "Detener servicios: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_info "Deteniendo servicios..."
        docker-compose -f "$COMPOSE_FILE" down
        show_success "Servicios detenidos"
    else
        show_info "Servicios siguen corriendo en segundo plano"
    fi
    
    exit 0
}

trap cleanup_on_exit SIGINT SIGTERM

# Ejecutar función principal
main "$@"