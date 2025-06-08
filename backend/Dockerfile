# =============================================================================
# DOCKERFILE BACKEND - PROYECTO FELICITA (CORREGIDO)
# Sistema de Facturación Electrónica para Perú
# =============================================================================

# =============================================================================
# STAGE 1: BASE IMAGE
# =============================================================================
FROM python:3.11-slim AS base

# Metadatos
LABEL maintainer="FELICITA Development Team"
LABEL description="Backend Django para Sistema de Facturación Electrónica FELICITA"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r felicita && useradd --no-log-init -r -g felicita felicita

# Crear directorios
RUN mkdir -p /app /app/logs /app/media /app/staticfiles && \
    chown -R felicita:felicita /app

# Establecer directorio de trabajo
WORKDIR /app

# =============================================================================
# STAGE 2: DEPENDENCIES
# =============================================================================
FROM base AS dependencies

# Copiar requirements
COPY requirements.txt /app/

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# STAGE 3: DEVELOPMENT
# =============================================================================
FROM dependencies AS development

# Instalar dependencias adicionales para desarrollo
RUN pip install \
    django-debug-toolbar \
    django-extensions \
    ipython \
    pytest \
    pytest-django \
    coverage

# Copiar código fuente
COPY . /app/

# Establecer permisos
RUN chown -R felicita:felicita /app

# Crear script de entrypoint para desarrollo
RUN cat > /entrypoint-dev.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 FELICITA Backend - Modo Desarrollo"

# Esperar a PostgreSQL
echo "⏳ Esperando a PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done
echo "✅ PostgreSQL está listo"

# Aplicar migraciones
echo "🔄 Aplicando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📦 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Ejecutar comando
echo "🎯 Ejecutando: $@"
exec "$@"
EOF

RUN chmod +x /entrypoint-dev.sh

# Cambiar a usuario no-root
USER felicita

# Puerto por defecto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Punto de entrada
ENTRYPOINT ["/entrypoint-dev.sh"]

# Comando por defecto para desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =============================================================================
# STAGE 4: PRODUCTION
# =============================================================================
FROM dependencies AS production

# Variables de producción
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Copiar código fuente
COPY . /app/

# Establecer permisos
RUN chown -R felicita:felicita /app

# Crear script de entrypoint para producción
RUN cat > /entrypoint-prod.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 FELICITA Backend - Modo Producción"

# Esperar a PostgreSQL
while ! nc -z ${DB_HOST} ${DB_PORT}; do
  sleep 1
done

# Aplicar migraciones
python manage.py migrate --noinput

# Recopilar archivos estáticos
python manage.py collectstatic --noinput --clear

# Ejecutar comando
exec "$@"
EOF

RUN chmod +x /entrypoint-prod.sh

# Cambiar a usuario no-root
USER felicita

# Punto de entrada
ENTRYPOINT ["/entrypoint-prod.sh"]

# Comando por defecto para producción
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]