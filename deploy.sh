#!/bin/bash
# Bash скрипт для развертывания на локальном сервере Linux
# Использование: ./deploy.sh [command]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функции для вывода
info() {
    echo -e "${CYAN}$1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Проверка Docker
check_docker() {
    info "Проверка установки Docker..."
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        success "Docker установлен: $(docker --version)"
        success "Docker Compose установлен: $(docker-compose --version)"
        return 0
    else
        error "Docker не установлен или не доступен"
        error "Установите Docker: https://docs.docker.com/get-docker/"
        return 1
    fi
}

# Проверка файла .env
check_env_file() {
    info "Проверка файла конфигурации .env..."
    if [ ! -f ".env" ]; then
        warning "Файл .env не найден!"
        if [ -f "env.production.template" ]; then
            info "Создание .env из шаблона..."
            cp env.production.template .env
            warning "ВАЖНО: Отредактируйте файл .env и установите SECRET_KEY и CORS_ORIGINS!"
            read -p "Нажмите Enter после редактирования .env..."
        else
            error "Шаблон env.production.template не найден!"
            return 1
        fi
    fi
    
    # Проверка SECRET_KEY
    if grep -q "SECRET_KEY=CHANGE_THIS" .env || grep -q "^SECRET_KEY=$" .env; then
        error "SECRET_KEY не настроен в .env файле!"
        error "Сгенерируйте ключ: python3 -c 'import secrets; print(secrets.token_urlsafe(32))'"
        return 1
    fi
    
    success "Файл .env найден и настроен"
    return 0
}

# Сборка и запуск
build_and_start() {
    info "Запуск развертывания..."
    
    if ! check_docker; then
        exit 1
    fi
    
    if ! check_env_file; then
        exit 1
    fi
    
    info "Сборка и запуск контейнеров..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    if [ $? -eq 0 ]; then
        success "Сервисы запущены успешно!"
        info "Ожидание готовности сервисов (30 секунд)..."
        sleep 30
        
        info "Проверка статуса сервисов..."
        docker-compose -f docker-compose.prod.yml ps
        
        info "Проверка health endpoints..."
        if curl -f -s http://localhost:8000/api/v1/health > /dev/null; then
            success "Backend доступен"
        else
            warning "Backend еще не готов, подождите немного..."
        fi
        
        success "\nРазвертывание завершено!"
        info "Frontend доступен по адресу: http://YOUR_SERVER_IP"
        info "Backend API доступен по адресу: http://YOUR_SERVER_IP/api/v1"
    else
        error "Ошибка при запуске сервисов"
        info "Просмотр логов: ./deploy.sh logs"
    fi
}

# Остановка
stop() {
    info "Остановка сервисов..."
    docker-compose -f docker-compose.prod.yml down
    success "Сервисы остановлены"
}

# Перезапуск
restart() {
    info "Перезапуск сервисов..."
    docker-compose -f docker-compose.prod.yml restart
    success "Сервисы перезапущены"
}

# Просмотр логов
logs() {
    if [ -n "$1" ]; then
        info "Логи сервиса: $1"
        docker-compose -f docker-compose.prod.yml logs -f "$1"
    else
        info "Логи всех сервисов (Ctrl+C для выхода)..."
        docker-compose -f docker-compose.prod.yml logs -f
    fi
}

# Статус
status() {
    info "Статус сервисов:"
    docker-compose -f docker-compose.prod.yml ps
    
    info "\nИспользование ресурсов:"
    docker stats --no-stream
}

# Обновление
update() {
    info "Обновление проекта..."
    
    info "Получение последних изменений из Git..."
    git pull origin main || warning "Не удалось обновить код из Git"
    
    info "Пересборка и перезапуск сервисов..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    success "Проект обновлен"
}

# Резервное копирование
backup() {
    backup_dir="backups"
    mkdir -p "$backup_dir"
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_path="$backup_dir/mongodb_backup_$timestamp"
    
    info "Создание резервной копии MongoDB..."
    info "Путь: $backup_path"
    
    docker-compose -f docker-compose.prod.yml exec -T mongodb mongodump --out "/data/backup/$timestamp"
    
    if [ $? -eq 0 ]; then
        success "Резервная копия создана: $backup_path"
    else
        error "Ошибка при создании резервной копии"
    fi
}

# Показать меню
show_menu() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}  HH Resume Analyzer - Deployment Tool${NC}"
    echo -e "${CYAN}========================================${NC}\n"
    
    echo "Доступные команды:"
    echo "  build      - Сборка и запуск сервисов"
    echo "  start      - Запуск сервисов"
    echo "  stop       - Остановка сервисов"
    echo "  restart    - Перезапуск сервисов"
    echo "  logs       - Просмотр логов (logs [service_name])"
    echo "  status     - Статус сервисов"
    echo "  update     - Обновление проекта из Git"
    echo "  backup     - Резервное копирование базы данных"
    echo ""
    echo "Примеры:"
    echo "  ./deploy.sh build"
    echo "  ./deploy.sh logs backend"
    echo "  ./deploy.sh status"
}

# Основная логика
case "${1:-menu}" in
    build)
        build_and_start
        ;;
    start)
        docker-compose -f docker-compose.prod.yml up -d
        success "Сервисы запущены"
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$2"
        ;;
    status)
        status
        ;;
    update)
        update
        ;;
    backup)
        backup
        ;;
    menu|*)
        show_menu
        ;;
esac
