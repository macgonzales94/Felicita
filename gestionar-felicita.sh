#!/bin/bash

# =============================================================================
# SCRIPT DE GESTIÓN DIARIA - PROYECTO FELICITA
# Operaciones rápidas para desarrollo diario
# =============================================================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

COMPOSE_FILE="docker-compose.dev.yml"

# Funciones de mensajes
show_success() { echo -e "${GREEN}✅ $1${NC}"; }
show_error() { echo -e "${RED}❌ $1${NC}"; }
show_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
show_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Función para mostrar el menú
show_menu() {
    clear
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "🛠️  FELICITA - GESTIÓN DIARIA"
    echo "============================================================================="
    echo -e "${NC}"
    echo -e "${GREEN}1)${NC} 🚀 Iniciar todos los servicios"
    echo -e "${GREEN}2)${NC} ⏹️  Detener todos los servicios"
    echo -e "${GREEN}3)${NC} 🔄 Reiniciar servicios"
    echo -e "${GREEN}4)${NC} 📊 Ver estado de servicios"
    echo -e "${GREEN}5)${NC} 📋 Ver logs en tiempo real"
    echo -e "${GREEN}6)${NC} 🗄️  Gestión de base de datos"
    echo -e "${GREEN}7)${NC} 🧹 Limpiar y resetear"
    echo -e "${GREEN}8)${NC} 🌐 Mostrar URLs y credenciales"
    echo -e "${GREEN}9)${NC} 🚪 Salir"
    echo ""
    read -p "Selecciona una opción (1-9): " choice
}

# Función para iniciar servicios
start_services() {
    show_info "Iniciando servicios FELICITA..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    show_info "Esperando que los servicios estén listos..."
    sleep 15
    
    # Verificar estado
    if curl -s http://localhost:8000/health/ >/dev/null 2>&1; then
        show_success "Backend disponible en http://localhost:8000"
    else
        show_warning "Backend aún no está listo"
    fi
    
    if curl -s http://localhost:5173/ >/dev/null 2>&1; then
        show_success "Frontend disponible en http://localhost:5173"
    else
        show_warning "Frontend aún no está listo"
    fi
}

# Función para detener servicios
stop_services() {
    show_info "Deteniendo servicios FELICITA..."
    docker-compose -f "$COMPOSE_FILE" down
    show_success "Servicios detenidos"
}

# Función para reiniciar servicios
restart_services() {
    echo -e "${YELLOW}¿Qué servicios quieres reiniciar?${NC}"
    echo "1) Todos los servicios"
    echo "2) Solo backend"
    echo "3) Solo frontend"
    echo "4) Solo base de datos"
    read -p "Selecciona (1-4): " restart_choice
    
    case $restart_choice in
        1)
            show_info "Reiniciando todos los servicios..."
            docker-compose -f "$COMPOSE_FILE" restart
            ;;
        2)
            show_info "Reiniciando backend..."
            docker-compose -f "$COMPOSE_FILE" restart backend
            ;;
        3)
            show_info "Reiniciando frontend..."
            docker-compose -f "$COMPOSE_FILE" restart frontend
            ;;
        4)
            show_info "Reiniciando base de datos..."
            docker-compose -f "$COMPOSE_FILE" restart db
            ;;
        *)
            show_error "Opción inválida"
            return
            ;;
    esac
    
    show_success "Reinicio completado"
}

# Función para mostrar estado
show_status() {
    show_info "Estado de los servicios:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    show_info "Verificando conectividad..."
    
    # Health checks
    if curl -s http://localhost:8000/health/ >/dev/null 2>&1; then
        echo -e "   ✅ Backend API: ${GREEN}Online${NC}"
    else
        echo -e "   ❌ Backend API: ${RED}Offline${NC}"
    fi
    
    if curl -s http://localhost:5173/ >/dev/null 2>&1; then
        echo -e "   ✅ Frontend: ${GREEN}Online${NC}"
    else
        echo -e "   ❌ Frontend: ${RED}Offline${NC}"
    fi
    
    if docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready >/dev/null 2>&1; then
        echo -e "   ✅ PostgreSQL: ${GREEN}Online${NC}"
    else
        echo -e "   ❌ PostgreSQL: ${RED}Offline${NC}"
    fi
    
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
        echo -e "   ✅ Redis: ${GREEN}Online${NC}"
    else
        echo -e "   ❌ Redis: ${RED}Offline${NC}"
    fi
}

# Función para ver logs
show_logs() {
    echo -e "${YELLOW}¿De qué servicio quieres ver los logs?${NC}"
    echo "1) Todos los servicios"
    echo "2) Backend"
    echo "3) Frontend" 
    echo "4) Base de datos"
    echo "5) Redis"
    read -p "Selecciona (1-5): " log_choice
    
    case $log_choice in
        1)
            show_info "Mostrando logs de todos los servicios..."
            docker-compose -f "$COMPOSE_FILE" logs -f
            ;;
        2)
            show_info "Mostrando logs del backend..."
            docker-compose -f "$COMPOSE_FILE" logs -f backend
            ;;
        3)
            show_info "Mostrando logs del frontend..."
            docker-compose -f "$COMPOSE_FILE" logs -f frontend
            ;;
        4)
            show_info "Mostrando logs de la base de datos..."
            docker-compose -f "$COMPOSE_FILE" logs -f db
            ;;
        5)
            show_info "Mostrando logs de Redis..."
            docker-compose -f "$COMPOSE_FILE" logs -f redis
            ;;
        *)
            show_error "Opción inválida"
            ;;
    esac
}

# Función para gestión de base de datos
manage_database() {
    echo -e "${YELLOW}Gestión de Base de Datos:${NC}"
    echo "1) Aplicar migraciones"
    echo "2) Crear superusuario"
    echo "3) Abrir shell de Django"
    echo "4) Backup de base de datos"
    echo "5) Resetear base de datos"
    read -p "Selecciona (1-5): " db_choice
    
    case $db_choice in
        1)
            show_info "Aplicando migraciones..."
            docker-compose -f "$COMPOSE_FILE" exec backend python manage.py migrate
            ;;
        2)
            show_info "Creando superusuario..."
            docker-compose -f "$COMPOSE_FILE" exec backend python manage.py createsuperuser
            ;;
        3)
            show_info "Abriendo shell de Django..."
            docker-compose -f "$COMPOSE_FILE" exec backend python manage.py shell
            ;;
        4)
            show_info "Creando backup..."
            BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
            docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U felicita_user felicita_dev > "$BACKUP_FILE"
            show_success "Backup creado: $BACKUP_FILE"
            ;;
        5)
            show_warning "¿Estás seguro? Se perderán todos los datos (y/n)"
            read -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                show_info "Reseteando base de datos..."
                docker-compose -f "$COMPOSE_FILE" down -v
                docker-compose -f "$COMPOSE_FILE" up -d db
                sleep 10
                docker-compose -f "$COMPOSE_FILE" up -d backend
                sleep 15
                docker-compose -f "$COMPOSE_FILE" exec backend python manage.py migrate
                show_success "Base de datos reseteada"
            fi
            ;;
    esac
}

# Función para limpiar y resetear
clean_reset() {
    echo -e "${YELLOW}Opciones de limpieza:${NC}"
    echo "1) Limpiar logs de Docker"
    echo "2) Limpiar imágenes no utilizadas"
    echo "3) Resetear todo FELICITA (¡CUIDADO!)"
    echo "4) Limpiar cache de npm (frontend)"
    read -p "Selecciona (1-4): " clean_choice
    
    case $clean_choice in
        1)
            show_info "Limpiando logs de Docker..."
            docker system prune --force
            show_success "Logs limpiados"
            ;;
        2)
            show_info "Limpiando imágenes no utilizadas..."
            docker image prune -f
            show_success "Imágenes limpiadas"
            ;;
        3)
            show_warning "¿Estás COMPLETAMENTE seguro? Se perderán TODOS los datos (y/n)"
            read -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                show_info "Reseteando todo FELICITA..."
                docker-compose -f "$COMPOSE_FILE" down -v --rmi all
                docker system prune -f
                show_success "Reset completo realizado"
                show_info "Ejecuta el script de inicialización para configurar de nuevo"
            fi
            ;;
        4)
            show_info "Limpiando cache de npm..."
            docker-compose -f "$COMPOSE_FILE" exec frontend npm cache clean --force
            show_success "Cache de npm limpiado"
            ;;
    esac
}

# Función para mostrar URLs
show_urls() {
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "🌐 URLS Y CREDENCIALES FELICITA"
    echo "============================================================================="
    echo -e "${NC}"
    echo -e "${GREEN}Aplicación Principal:${NC}"
    echo "   🖥️  Frontend: http://localhost:5173"
    echo "   🔧 Backend API: http://localhost:8000/api"
    echo "   📋 Admin Django: http://localhost:8000/admin"
    echo ""
    echo -e "${GREEN}Herramientas:${NC}"
    echo "   🗄️  PgAdmin: http://localhost:5050"
    echo "   📧 MailHog: http://localhost:8025"
    echo "   🌸 Flower: http://localhost:5555"
    echo ""
    echo -e "${YELLOW}Credenciales:${NC}"
    echo -e "${GREEN}FELICITA:${NC}"
    echo "   📧 admin@felicita.pe / admin123"
    echo "   📧 contador@felicita.pe / contador123"
    echo "   📧 vendedor@felicita.pe / vendedor123"
    echo ""
    echo -e "${GREEN}PgAdmin:${NC} admin@felicita.dev / admin123"
    echo -e "${GREEN}Flower:${NC} admin / flower123"
}

# Loop principal
main() {
    while true; do
        show_menu
        
        case $choice in
            1)
                start_services
                ;;
            2)
                stop_services
                ;;
            3)
                restart_services
                ;;
            4)
                show_status
                ;;
            5)
                show_logs
                ;;
            6)
                manage_database
                ;;
            7)
                clean_reset
                ;;
            8)
                show_urls
                ;;
            9)
                show_info "¡Hasta luego!"
                exit 0
                ;;
            *)
                show_error "Opción inválida"
                ;;
        esac
        
        echo ""
        read -p "Presiona Enter para continuar..."
    done
}

# Ejecutar función principal
main