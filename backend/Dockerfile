# =============================================================================
# DOCKERFILE BACKEND - PROYECTO FELICITA
# =============================================================================

FROM python:3.11-slim AS base

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    pkg-config \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios y preparar permisos para logs
RUN mkdir -p /app /app/logs /app/media /app/staticfiles && \
    chmod -R 777 /app/logs && \
    touch /app/logs/felicita_dev.log && chmod 666 /app/logs/felicita_dev.log

WORKDIR /app

# =============================================================================
# STAGE: DEPENDENCIES
# =============================================================================
FROM base AS dependencies

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# =============================================================================
# STAGE: DEVELOPMENT
# =============================================================================
FROM dependencies AS development

ENV DJANGO_SETTINGS_MODULE=config.settings.local
ENV DEBUG=True

# Instalar dependencias de desarrollo
RUN pip install \
    django-debug-toolbar \
    django-extensions \
    ipython \
    pytest \
    pytest-django

# Copiar código
COPY . /app/

# Copiar script de entrada
COPY docker/entrypoint-dev.sh /entrypoint-dev.sh
RUN chmod +x /entrypoint-dev.sh

EXPOSE 8000

CMD ["/entrypoint-dev.sh"]
