# =============================================================================
# DOCKERFILE FRONTEND - PROYECTO FELICITA
# Sistema de Facturación Electrónica para Perú
# 
# Multi-stage build para optimizar el tamaño de la imagen
# =============================================================================

# =============================================================================
# STAGE 1: BUILD
# =============================================================================
FROM node:18-alpine AS builder

# Metadatos
LABEL maintainer="FELICITA Development Team"
LABEL description="Frontend React para Sistema de Facturación Electrónica FELICITA"
LABEL version="1.0.0"

# Variables de entorno para el build
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV DISABLE_ESLINT_PLUGIN=true

# Instalar dependencias del sistema
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package.json package-lock.json* ./

# Instalar dependencias con cache optimizado
RUN npm ci --only=production --silent && \
    npm cache clean --force

# Copiar código fuente
COPY . .

# Construir aplicación para producción
RUN npm run build

# Limpiar archivos innecesarios
RUN rm -rf node_modules \
    src \
    public \
    *.json \
    *.js \
    *.ts \
    *.md

# =============================================================================
# STAGE 2: PRODUCTION
# =============================================================================
FROM nginx:1.25-alpine AS production

# Metadatos
LABEL stage="production"

# Variables de entorno
ENV NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/templates
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d

# Variables configurables para nginx
ENV API_URL=http://backend:8000
ENV CLIENT_MAX_BODY_SIZE=50M
ENV GZIP_ENABLED=on
ENV CACHE_CONTROL_MAX_AGE=31536000

# Instalar dependencias adicionales
RUN apk add --no-cache \
    curl \
    tzdata \
    && rm -rf /var/cache/apk/*

# Configurar zona horaria para Perú
ENV TZ=America/Lima
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S felicita && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G felicita -g felicita felicita

# Copiar archivos construidos desde stage builder
COPY --from=builder --chown=felicita:felicita /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de nginx
COPY --chown=felicita:felicita nginx/nginx.conf /etc/nginx/nginx.conf
COPY --chown=felicita:felicita nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --chown=felicita:felicita nginx/security.conf /etc/nginx/conf.d/security.conf
COPY --chown=felicita:felicita nginx/compression.conf /etc/nginx/conf.d/compression.conf

# Crear directorios necesarios
RUN mkdir -p /var/cache/nginx /var/log/nginx /var/run/nginx && \
    chown -R felicita:felicita /var/cache/nginx /var/log/nginx /var/run/nginx /etc/nginx/conf.d

# Configurar permisos
RUN chmod 755 /usr/share/nginx/html && \
    find /usr/share/nginx/html -type f -exec chmod 644 {} \; && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \;

# Script de inicio personalizado
COPY --chown=felicita:felicita docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Crear página de health check
RUN echo '{"status":"healthy","service":"felicita-frontend","timestamp":"'$(date -Iseconds)'"}' > /usr/share/nginx/html/health.json

# Cambiar a usuario no-root
USER felicita

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health.json || exit 1

# Comando de inicio
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# CONFIGURACIÓN ADICIONAL PARA DESARROLLO
# =============================================================================

# Stage para desarrollo
FROM node:18-alpine AS development

# Variables de entorno para desarrollo
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Instalar dependencias del sistema
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++

# Crear directorio de trabajo
WORKDIR /app

# Crear usuario para desarrollo
RUN addgroup -g 1001 -S felicita && \
    adduser -S -D -H -u 1001 -h /app -s /bin/sh -G felicita -g felicita felicita && \
    chown -R felicita:felicita /app

# Cambiar a usuario no-root
USER felicita

# Exponer puerto de desarrollo
EXPOSE 5173

# Comando para desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# =============================================================================
# ARCHIVOS DE CONFIGURACIÓN NGINX
# =============================================================================

# nginx/nginx.conf
# worker_processes auto;
# error_log /var/log/nginx/error.log notice;
# pid /var/run/nginx/nginx.pid;
# 
# events {
#     worker_connections 1024;
#     use epoll;
#     multi_accept on;
# }
# 
# http {
#     include /etc/nginx/mime.types;
#     default_type application/octet-stream;
# 
#     # Logging
#     log_format main '$remote_addr - $remote_user [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for"';
#     access_log /var/log/nginx/access.log main;
# 
#     # Performance
#     sendfile on;
#     tcp_nopush on;
#     tcp_nodelay on;
#     keepalive_timeout 65;
#     types_hash_max_size 2048;
#     client_max_body_size ${CLIENT_MAX_BODY_SIZE};
# 
#     # Security
#     server_tokens off;
#     add_header X-Frame-Options DENY;
#     add_header X-Content-Type-Options nosniff;
#     add_header X-XSS-Protection "1; mode=block";
# 
#     # Include configurations
#     include /etc/nginx/conf.d/*.conf;
# }

# nginx/default.conf.template
# server {
#     listen 80;
#     server_name localhost;
#     root /usr/share/nginx/html;
#     index index.html;
# 
#     # API Proxy
#     location /api/ {
#         proxy_pass ${API_URL}/api/;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#         proxy_read_timeout 90;
#         proxy_connect_timeout 90;
#         proxy_redirect off;
#     }
# 
#     # Static files with cache
#     location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
#         expires ${CACHE_CONTROL_MAX_AGE}s;
#         add_header Cache-Control "public, immutable";
#         add_header Vary Accept-Encoding;
#     }
# 
#     # SPA routing
#     location / {
#         try_files $uri $uri/ /index.html;
#         add_header Cache-Control "no-cache, no-store, must-revalidate";
#         add_header Pragma "no-cache";
#         add_header Expires "0";
#     }
# 
#     # Health check
#     location /health {
#         access_log off;
#         return 200 "healthy\n";
#         add_header Content-Type text/plain;
#     }
# 
#     # Error pages
#     error_page 404 /index.html;
#     error_page 500 502 503 504 /50x.html;
#     location = /50x.html {
#         root /usr/share/nginx/html;
#     }
# }

# docker-entrypoint.sh
# #!/bin/sh
# set -e
# 
# # Función de logging
# log() {
#     echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
# }
# 
# # Función de configuración
# configure_nginx() {
#     log "Configurando nginx para FELICITA Frontend..."
#     
#     # Reemplazar variables de entorno en templates
#     envsubst '$API_URL $CLIENT_MAX_BODY_SIZE $CACHE_CONTROL_MAX_AGE' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
#     
#     # Validar configuración
#     nginx -t
#     
#     log "Configuración de nginx completada"
# }
# 
# # Función de health check
# health_check() {
#     log "Verificando estado del servicio..."
#     
#     # Actualizar timestamp en health.json
#     echo '{"status":"healthy","service":"felicita-frontend","timestamp":"'$(date -Iseconds)'","version":"1.0.0"}' > /usr/share/nginx/html/health.json
#     
#     log "Health check configurado"
# }
# 
# # Función principal
# main() {
#     log "Iniciando FELICITA Frontend..."
#     log "Versión: 1.0.0"
#     log "Ambiente: production"
#     log "API URL: ${API_URL}"
#     
#     # Configurar nginx
#     configure_nginx
#     
#     # Configurar health check
#     health_check
#     
#     log "Frontend listo para recibir conexiones"
#     
#     # Ejecutar comando principal
#     exec "$@"
# }
# 
# # Ejecutar función principal
# main

# =============================================================================
# INSTRUCCIONES DE BUILD
# =============================================================================

# Para construir imagen de producción:
# docker build --target production -t felicita-frontend:latest .

# Para construir imagen de desarrollo:
# docker build --target development -t felicita-frontend:dev .

# Para ejecutar contenedor de producción:
# docker run -d -p 80:80 --name felicita-frontend felicita-frontend:latest

# Para ejecutar contenedor de desarrollo:
# docker run -d -p 5173:5173 -v $(pwd):/app --name felicita-frontend-dev felicita-frontend:dev

# =============================================================================
# OPTIMIZACIONES APLICADAS
# =============================================================================

# 1. Multi-stage build para reducir tamaño de imagen
# 2. Usuario no-root para seguridad
# 3. Health check incorporado
# 4. Configuración nginx optimizada
# 5. Cache de archivos estáticos
# 6. Compresión gzip
# 7. Headers de seguridad
# 8. Proxy reverso para API
# 9. Manejo de SPA routing
# 10. Logs estructurados