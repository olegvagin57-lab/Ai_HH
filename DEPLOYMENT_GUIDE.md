# Руководство по развертыванию в продакшн

## Предварительные требования

1. **Сервер** с Docker и Docker Compose
2. **MongoDB** (можно использовать встроенный в docker-compose)
3. **Redis** (можно использовать встроенный в docker-compose)
4. **Домен** и SSL сертификат (рекомендуется Let's Encrypt)

## Шаги развертывания

### 1. Подготовка окружения

```bash
# Клонировать репозиторий
git clone <repository-url>
cd HH_AI

# Создать .env файл из примера
cp backend/.env.example backend/.env
```

### 2. Настройка переменных окружения

Отредактируйте `backend/.env`:

```env
# КРИТИЧНО: Сгенерируйте безопасный секретный ключ
SECRET_KEY=$(openssl rand -hex 32)

# MongoDB
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DATABASE=hh_analyzer

# Redis
REDIS_URL=redis://redis:6379

# Cloudflare Worker
CLOUDFLARE_WORKER_URL=https://your-worker.workers.dev

# Production настройки
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com

# Логирование
LOG_FORMAT=json
LOG_FILE=/var/log/hh_analyzer/app.log
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### 3. Генерация секретного ключа

```bash
# Linux/Mac
openssl rand -hex 32

# Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### 4. Сборка и запуск

```bash
# Сборка образов
docker-compose build

# Запуск сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
```

### 5. Настройка Nginx (рекомендуется)

Создайте конфигурацию Nginx:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com
```

### 7. Настройка резервного копирования

Добавьте в crontab:

```bash
# Ежедневное резервное копирование в 2:00
0 2 * * * /path/to/scripts/backup_mongodb.sh
```

### 8. Мониторинг

#### Health Checks

```bash
# Проверка здоровья API
curl http://localhost:8000/health

# Проверка готовности
curl http://localhost:8000/health/ready

# Проверка жизнеспособности
curl http://localhost:8000/health/live
```

#### Логи

```bash
# Просмотр логов backend
docker-compose logs -f backend

# Просмотр логов MongoDB
docker-compose logs -f mongodb

# Просмотр логов Redis
docker-compose logs -f redis
```

## Обслуживание

### Резервное копирование

```bash
# Ручное резервное копирование
./scripts/backup_mongodb.sh

# Восстановление из backup
./scripts/restore_mongodb.sh /path/to/backup.tar.gz
```

### Обновление

```bash
# Остановка сервисов
docker-compose down

# Обновление кода
git pull

# Пересборка образов
docker-compose build --no-cache

# Запуск
docker-compose up -d
```

### Масштабирование

Для горизонтального масштабирования:

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
```

## Безопасность

### Чек-лист безопасности

- [ ] Секретный ключ изменен с дефолтного значения
- [ ] DEBUG=false в продакшн
- [ ] CORS настроен только для вашего домена
- [ ] HTTPS включен
- [ ] Firewall настроен (только необходимые порты)
- [ ] Регулярные обновления безопасности
- [ ] Мониторинг логов на подозрительную активность
- [ ] Резервное копирование настроено

### Рекомендации

1. **Не храните секреты в коде** - используйте переменные окружения
2. **Используйте секретный менеджер** (AWS Secrets Manager, HashiCorp Vault)
3. **Регулярно обновляйте зависимости** - `pip list --outdated`
4. **Мониторьте логи** на ошибки и подозрительную активность
5. **Настройте алерты** на критические ошибки

## Troubleshooting

### Проблема: MongoDB не подключается

```bash
# Проверка статуса
docker-compose ps mongodb

# Проверка логов
docker-compose logs mongodb

# Перезапуск
docker-compose restart mongodb
```

### Проблема: Rate limiting слишком строгий

Отредактируйте `backend/.env`:
```env
RATE_LIMIT_PER_MINUTE=120
RATE_LIMIT_PER_HOUR=2000
```

### Проблема: Высокая нагрузка

1. Увеличьте количество workers в `docker-compose.yml`
2. Настройте Redis для кэширования
3. Оптимизируйте запросы к БД

## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Проверьте health checks
3. Проверьте конфигурацию `.env`
4. Создайте issue в репозитории
