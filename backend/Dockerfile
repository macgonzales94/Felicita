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
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario
RUN groupadd -r felicita && useradd --no-log-init -r -g felicita felicita

# Crear directorios
RUN mkdir -p /app /app/logs /app/media /app/staticfiles && \
    chown -R felicita:felicita /app && \
    chmod -R 755 /app/logs

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
RUN chown -R felicita:felicita /app

# Copiar script de entrada
COPY --chown=felicita:felicita docker/entrypoint-dev.sh /entrypoint-dev.sh
RUN chmod +x /entrypoint-dev.sh

USER felicita

EXPOSE 8000

CMD ["/entrypoint-dev.sh"]