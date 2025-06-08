#!/bin/sh
# =============================================================================
# ENTRYPOINT DESARROLLO - PROYECTO FELICITA
# Sistema de Facturación Electrónica para Perú
# =============================================================================

set -e

# Función de logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] FELICITA: $1"
}

# Función para esperar a que PostgreSQL esté listo
wait_for_postgres() {
    log "Esperando a que PostgreSQL esté disponible..."
    while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
        log "PostgreSQL no está disponible - durmiendo"
        sleep 1
    done
    log "PostgreSQL está disponible"
}

# Función para esperar a que Redis esté listo
wait_for_redis() {
    log "Esperando a que Redis esté disponible..."
    REDIS_HOST=${REDIS_HOST:-redis}
    REDIS_PORT=${REDIS_PORT:-6379}
    while ! nc -z $REDIS_HOST $REDIS_PORT; do
        log "Redis no está disponible - durmiendo"
        sleep 1
    done
    log "Redis está disponible"
}

# Función para aplicar migraciones
apply_migrations() {
    log "Aplicando migraciones de Django..."
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    log "Migraciones aplicadas correctamente"
}

# Función para crear superusuario de desarrollo
create_superuser() {
    log "Verificando/creando superusuario de desarrollo..."

    python manage.py shell << PYTHON_EOF
from django.contrib.auth import get_user_model
from aplicaciones.core.models import Empresa

User = get_user_model()

# Verificar o crear empresa base
empresa, _ = Empresa.objects.get_or_create(
    id=1,
    defaults={
        "razon_social": "EMPRESA FELICITA SAC",
        "ruc": "20123456789",
        "direccion": "Av. Principal 123",
    }
)

# Crear superusuario si no existe
if not User.objects.filter(email="admin@felicita.pe").exists():
    usuario = User.objects.create_superuser(
        email="admin@felicita.pe",
        username="admin",
        password="admin123",
        nombres="Administrador",
        apellido_paterno="Sistema",
        apellido_materno="FELICITA",
        numero_documento="12345678",
        tipo_documento="DNI",
        empresa=empresa  # ← IMPORTANTE: sin comillas
    )
    print("✅ Superusuario creado:", usuario)
else:
    print("🟢 Superusuario ya existe.")
PYTHON_EOF

    log "Superusuario verificado/creado"
}

# Función principal de inicialización
initialize() {
    log "Iniciando FELICITA Backend en modo desarrollo..."
    wait_for_postgres
    wait_for_redis
    apply_migrations
    create_superuser
    log "Inicialización completada"
}

# Función para iniciar servidor de desarrollo
start_development_server() {
    log "Iniciando servidor de desarrollo Django..."
    log "Servidor disponible en: http://0.0.0.0:8000"
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

# Función principal
main() {
    if [ "$1" != "help" ]; then
        initialize
    fi

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
        *)
            start_development_server
            ;;
    esac
}

main "$@"

set -e