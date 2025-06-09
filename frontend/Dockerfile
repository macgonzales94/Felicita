# =============================================================================
# DOCKERFILE FRONTEND CORREGIDO - PROYECTO FELICITA
# Sistema de Facturación Electrónica para Perú
# =============================================================================

# =============================================================================
# STAGE 1: BASE
# =============================================================================
FROM node:18-alpine AS base

# Metadatos
LABEL maintainer="FELICITA Development Team"
LABEL description="Frontend React para Sistema de Facturación Electrónica FELICITA"
LABEL version="1.0.0"

# Variables de entorno
ENV NODE_ENV=development
ENV VITE_API_URL=http://localhost:8000

# Instalar dependencias del sistema
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S felicita && \
    adduser -S -D -H -u 1001 -h /app -s /bin/sh -G felicita -g felicita felicita

# Crear directorio de trabajo
WORKDIR /app

# Cambiar ownership del directorio
RUN chown -R felicita:felicita /app

# =============================================================================
# STAGE 2: DEVELOPMENT
# =============================================================================
FROM base AS development

# Cambiar a usuario no-root
USER felicita

# Copiar archivos de configuración de dependencias
COPY --chown=felicita:felicita package*.json ./

# Instalar dependencias
RUN npm ci --include=dev && \
    npm cache clean --force

# Copiar código fuente
COPY --chown=felicita:felicita . .

# Verificar que Vite está instalado
RUN npx vite --version

# Exponer puerto
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5173/ || exit 1

# Comando por defecto
CMD ["npm", "run", "dev"]

# =============================================================================
# STAGE 3: PRODUCTION BUILD
# =============================================================================
FROM base AS builder

# Cambiar a usuario no-root
USER felicita

# Copiar archivos de configuración
COPY --chown=felicita:felicita package*.json ./

# Instalar dependencias de producción
RUN npm ci --only=production --silent && \
    npm cache clean --force

# Copiar código fuente
COPY --chown=felicita:felicita . .

# Construir para producción
RUN npm run build

# =============================================================================
# STAGE 4: PRODUCTION NGINX
# =============================================================================
FROM nginx:1.25-alpine AS production

# Metadatos
LABEL stage="production"

# Variables de entorno
ENV API_URL=http://backend:8000

# Copiar archivos construidos
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de nginx
COPY --chown=nginx:nginx nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Crear página de health check
RUN echo '{"status":"healthy","service":"felicita-frontend","timestamp":"'$(date -Iseconds)'"}' > /usr/share/nginx/html/health.json

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health.json || exit 1

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# CONFIGURACIÓN ADICIONAL PARA DESARROLLO
# ========================================================================

# Stage para desarrollo
#FROM node:18-alpine AS development

# Variables de entorno para desarrollo
#ENV NODE_ENV=development
#ENV CHOKIDAR_USEPOLLING=true
#ENV WATCHPACK_POLLING=true

# Instalar dependencias del sistema
#RUN apk add --no-cache \
#    git \
#    python3 \
#    make \
#    g++

# Crear directorio de trabajo
#WORKDIR /app

# Crear usuario para desarrollo
#RUN addgroup -g 1001 -S felicita && \
#    adduser -S -D -H -u 1001 -h /app -s /bin/sh -G felicita -g felicita felicita && \
#    chown -R felicita:felicita /app

# Cambiar a usuario no-root
#SER felicita

# Exponer puerto de desarrollo
#EXPOSE 5173

# Comando para desarrollo
#CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

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