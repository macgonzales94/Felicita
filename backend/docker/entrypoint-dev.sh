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

# Verificar que el archivo de log exista
prepare_logs() {
    mkdir -p /app/logs
    touch /app/logs/felicita_dev.log
    chmod 666 /app/logs/felicita_dev.log
}

# Esperar a PostgreSQL
wait_for_postgres() {
    log "Esperando a que PostgreSQL esté disponible..."
    while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
        log "PostgreSQL no está disponible - durmiendo"
        sleep 1
    done
    log "PostgreSQL está disponible"
}

# Esperar a Redis
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

# Aplicar migraciones
apply_migrations() {
    log "Aplicando migraciones de Django..."
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    log "Migraciones aplicadas correctamente"
}

# Crear superusuario si no existe
create_superuser() {
    log "Verificando/creando superusuario de desarrollo..."
    python manage.py shell << PYTHON_EOF
from django.contrib.auth import get_user_model
from aplicaciones.core.models import Empresa

User = get_user_model()

empresa, _ = Empresa.objects.get_or_create(
    id=1,
    defaults={
        "razon_social": "EMPRESA FELICITA SAC",
        "ruc": "20123456789",
        "direccion": "Av. Principal 123",
    }
)

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
        empresa=empresa
    )
    print("✅ Superusuario creado:", usuario)
else:
    print("🟢 Superusuario ya existe.")
PYTHON_EOF

    log "Superusuario verificado/creado"
}

# Inicializar entorno
initialize() {
    log "Iniciando FELICITA Backend en modo desarrollo..."
    prepare_logs
    wait_for_postgres
    wait_for_redis
    apply_migrations
    create_superuser
    log "Inicialización completada"
}

# Iniciar servidor
start_development_server() {
    log "Iniciando servidor de desarrollo Django..."
    log "Servidor disponible en: http://0.0.0.0:8000"
    exec python manage.py runserver 0.0.0.0:8000
}

# Iniciar worker
start_celery_worker() {
    log "Iniciando Celery Worker..."
    exec celery -A config worker --loglevel=INFO --concurrency=2
}

# Iniciar beat
start_celery_beat() {
    log "Iniciando Celery Beat..."
    exec celery -A config beat --loglevel=INFO
}

# Entrada principal
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
