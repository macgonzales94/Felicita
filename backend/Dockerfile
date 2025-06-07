# =============================================================================
# DOCKERFILE BACKEND - PROYECTO FELICITA
# Sistema de Facturación Electrónica para Perú
# =============================================================================

# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="Equipo FELICITA <dev@felicita.pe>"
LABEL description="Backend API para FELICITA - Sistema de Facturación Electrónica"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    APP_HOME=/app \
    DJANGO_SETTINGS_MODULE=felicita.configuracion.produccion

# Crear usuario no-root para seguridad
RUN groupadd -r felicita && useradd -r -g felicita felicita

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    # Dependencias de PostgreSQL
    libpq-dev \
    # Dependencias de compilación
    gcc \
    g++ \
    # Utilidades
    curl \
    wget \
    git \
    # Dependencias para PIL/Pillow
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    # Dependencias para reportes PDF
    libfontconfig1 \
    libxrender1 \
    # Herramientas de sistema
    procps \
    # Limpiar cache
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios necesarios
RUN mkdir -p $APP_HOME \
    && mkdir -p $APP_HOME/static \
    && mkdir -p $APP_HOME/media \
    && mkdir -p $APP_HOME/logs \
    && mkdir -p $APP_HOME/backups \
    && chown -R felicita:felicita $APP_HOME

# Establecer directorio de trabajo
WORKDIR $APP_HOME

# Actualizar pip y instalar herramientas de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copiar requirements primero para aprovechar cache de Docker
COPY --chown=felicita:felicita requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY --chown=felicita:felicita . .

# Crear script de entrada
RUN cat > /entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Iniciando FELICITA Backend..."

# Función para esperar a que PostgreSQL esté listo
wait_for_db() {
    echo "⏳ Esperando a que PostgreSQL esté listo..."
    while ! python manage.py dbshell < /dev/null; do
        echo "⏳ PostgreSQL no está listo - esperando..."
        sleep 1
    done
    echo "✅ PostgreSQL está listo!"
}

# Función para aplicar migraciones
apply_migrations() {
    echo "📊 Aplicando migraciones de base de datos..."
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    echo "✅ Migraciones aplicadas!"
}

# Función para crear superusuario si no existe
create_superuser() {
    echo "👤 Verificando superusuario..."
    python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@felicita.pe',
        password='admin123',
        username='admin',
        nombres='Administrador',
        apellido_paterno='Sistema',
        apellido_materno='FELICITA',
        numero_documento='00000000'
    )
    print("✅ Superusuario creado: admin@felicita.pe / admin123")
else:
    print("ℹ️  Superusuario ya existe")
PYEOF
}

# Función para recopilar archivos estáticos
collect_static() {
    echo "📦 Recopilando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
    echo "✅ Archivos estáticos recopilados!"
}

# Función para cargar datos iniciales
load_initial_data() {
    if [ -f "fixtures/datos_iniciales.json" ]; then
        echo "📋 Cargando datos iniciales..."
        python manage.py loaddata fixtures/datos_iniciales.json || echo "⚠️  Datos iniciales ya cargados o error en carga"
    fi
}

# Función principal
main() {
    case "$1" in
        "development")
            echo "🔧 Modo desarrollo"
            wait_for_db
            apply_migrations
            create_superuser
            load_initial_data
            echo "🚀 Iniciando servidor de desarrollo..."
            python manage.py runserver 0.0.0.0:8000
            ;;
        "production")
            echo "🏭 Modo producción"
            wait_for_db
            apply_migrations
            collect_static
            create_superuser
            load_initial_data
            echo "🚀 Iniciando servidor Gunicorn..."
            gunicorn felicita.wsgi:application \
                --bind 0.0.0.0:8000 \
                --workers 3 \
                --worker-class sync \
                --worker-connections 1000 \
                --max-requests 1000 \
                --max-requests-jitter 50 \
                --timeout 30 \
                --keep-alive 2 \
                --preload \
                --access-logfile - \
                --error-logfile - \
                --log-level info
            ;;
        "migrate")
            echo "📊 Solo migraciones"
            wait_for_db
            apply_migrations
            ;;
        "shell")
            echo "🐚 Iniciando shell"
            wait_for_db
            python manage.py shell
            ;;
        "test")
            echo "🧪 Ejecutando tests"
            python manage.py test
            ;;
        *)
            echo "🚀 Iniciando con comando personalizado: $@"
            exec "$@"
            ;;
    esac
}

# Ejecutar función principal con todos los argumentos
main "$@"
EOF

# Hacer el script ejecutable
RUN chmod +x /entrypoint.sh

# Cambiar al usuario no-root
USER felicita

# Exponer puerto
EXPOSE 8000

# Configurar healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Comando por defecto
ENTRYPOINT ["/entrypoint.sh"]
CMD ["production"]