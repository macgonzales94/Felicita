#!/bin/bash

# =============================================================================
# ENTRYPOINT DESARROLLO - PROYECTO FELICITA
# Sistema de Facturación Electrónica para Perú
# =============================================================================

set -e

# Colores para logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] FELICITA:${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] FELICITA:${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] FELICITA:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] FELICITA:${NC} $1"
}

# Función para esperar a que PostgreSQL esté listo
wait_for_postgres() {
    log "Esperando a que PostgreSQL esté disponible..."
    
    while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
        log "PostgreSQL no está disponible - durmiendo"
        sleep 1
    done
    
    log_success "PostgreSQL está disponible"
}

# Función para esperar a que Redis esté listo
wait_for_redis() {
    log "Esperando a que Redis esté disponible..."
    
    # Extraer host y puerto de REDIS_URL si está disponible
    if [ -n "$REDIS_URL" ]; then
        REDIS_HOST=$(echo $REDIS_URL | sed -n 's|redis://[^@]*@\([^:]*\):.*|\1|p')
        REDIS_PORT=$(echo $REDIS_URL | sed -n 's|redis://[^@]*@[^:]*:\([0-9]*\)/.*|\1|p')
    fi
    
    REDIS_HOST=${REDIS_HOST:-redis}
    REDIS_PORT=${REDIS_PORT:-6379}
    
    while ! nc -z $REDIS_HOST $REDIS_PORT; do
        log "Redis no está disponible - durmiendo"
        sleep 1
    done
    
    log_success "Redis está disponible"
}

# Función para aplicar migraciones
apply_migrations() {
    log "Aplicando migraciones de Django..."
    
    # Crear migraciones si no existen
    python manage.py makemigrations --noinput
    
    # Aplicar migraciones
    python manage.py migrate --noinput
    
    log_success "Migraciones aplicadas correctamente"
}

# Función para crear superusuario de desarrollo
create_superuser() {
    log "Verificando/creando superusuario de desarrollo..."
    
    python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()

email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@felicita.pe')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        nombres='Administrador',
        apellido_paterno='Sistema',
        apellido_materno='FELICITA',
        numero_documento='12345678',
        tipo_documento='DNI'
    )
    print(f'Superusuario creado: {email}')
else:
    print(f'Superusuario ya existe: {email}')
EOF
    
    log_success "Superusuario verificado/creado"
}

# Función para cargar datos iniciales
load_initial_data() {
    if [ -f "fixtures/datos_iniciales.json" ]; then
        log "Cargando datos iniciales..."
        python manage.py loaddata fixtures/datos_iniciales.json
        log_success "Datos iniciales cargados"
    else
        log_warning "No se encontraron datos iniciales para cargar"
    fi
}

# Función para configurar archivos estáticos en desarrollo
setup_static_files() {
    log "Configurando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
    log_success "Archivos estáticos configurados"
}

# Función principal de inicialización
initialize() {
    log "Iniciando FELICITA Backend en modo desarrollo..."
    log "Versión: 1.0.0"
    log "Ambiente: ${DJANGO_SETTINGS_MODULE:-development}"
    
    # Esperar servicios dependientes
    wait_for_postgres
    wait_for_redis
    
    # Configurar Django
    apply_migrations
    create_superuser
    load_initial_data
    setup_static_files
    
    log_success "Inicialización completada"
}

# Función para iniciar servidor de desarrollo
start_development_server() {
    log "Iniciando servidor de desarrollo Django..."
    log "Servidor disponible en: http://0.0.0.0:8000"
    log "API disponible en: http://0.0.0.0:8000/api"
    log "Admin disponible en: http://0.0.0.0:8000/admin"
    
    exec python manage.py runserver 0.0.0.0:8000
}

# Función para iniciar worker de Celery
start_celery_worker() {
    log "Iniciando Celery Worker..."
    exec celery -A config worker --loglevel=INFO --concurrency=2
}

# Función para iniciar beat de Celery
start_celery_beat() {
    log "Iniciando Celery Beat..."
    exec celery -A config beat --loglevel=INFO
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  server          Iniciar servidor de desarrollo (por defecto)"
    echo "  worker          Iniciar Celery worker"
    echo "  beat            Iniciar Celery beat scheduler"
    echo "  shell           Abrir shell de Django"
    echo "  migrate         Solo aplicar migraciones"
    echo "  test            Ejecutar tests"
    echo "  help            Mostrar esta ayuda"
    echo ""
}

# Función principal
main() {
    # Siempre inicializar (excepto para ayuda)
    if [ "$1" != "help" ]; then
        initialize
    fi
    
    # Ejecutar comando específico
    case "${1:-server}" in
        server)
            start_development_server
            ;;
        worker)
            start_celery_worker
            ;;
        beat)
            start_celery_beat
            ;;
        shell)
            log "Abriendo shell de Django..."
            exec python manage.py shell
            ;;
        migrate)
            log "Solo aplicando migraciones..."
            # La inicialización ya aplicó las migraciones
            ;;
        test)
            log "Ejecutando tests..."
            exec python manage.py test
            ;;
        help)
            show_help
            ;;
        *)
            log_error "Comando desconocido: $1"
            show_help
            exit 1
            ;;
    esac
}

# Manejo de señales para shutdown limpio
cleanup() {
    log "Deteniendo FELICITA Backend..."
    exit 0
}

trap cleanup SIGTERM SIGINT

# Ejecutar función principal
main "$@"