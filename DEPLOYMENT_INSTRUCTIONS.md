# 📋 Инструкция по развертыванию HH Resume Analyzer

## Для отдела развертывания

Этот документ содержит пошаговую инструкцию по развертыванию проекта HH Resume Analyzer на сервере компании.

---

## 📦 Требования к серверу

### Минимальные требования:
- **ОС**: Linux (Ubuntu 20.04+ / CentOS 7+ / Debian 10+) или Windows Server
- **CPU**: 4 ядра
- **RAM**: 8 GB
- **Диск**: 50 GB свободного места
- **Docker**: версия 20.10+
- **Docker Compose**: версия 1.29+

### Проверка установки Docker:
```bash
docker --version
docker-compose --version
```

Если Docker не установлен, установите по инструкции: https://docs.docker.com/get-docker/

---

## 🚀 Быстрое развертывание

### Шаг 1: Подготовка проекта

1. Скопируйте проект на сервер (через Git или архив)
2. Перейдите в директорию проекта:
   ```bash
   cd /path/to/HH_AI
   ```

### Шаг 2: Настройка переменных окружения

1. Создайте файл `.env` из шаблона:
   ```bash
   cp env.production.template .env
   ```

2. **ОБЯЗАТЕЛЬНО** отредактируйте файл `.env` и установите:
   - `SECRET_KEY` - сгенерируйте безопасный ключ (минимум 32 символа)
   - `CORS_ORIGINS` - укажите IP адрес или домен сервера
   - `MONGODB_URL` - если используете внешний MongoDB
   - `REDIS_URL` - если используете внешний Redis

   **Генерация SECRET_KEY:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   Или через PowerShell (Windows):
   ```powershell
   -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 48 | ForEach-Object {[char]$_})
   ```

3. **Пример настройки CORS_ORIGINS:**
   ```
   CORS_ORIGINS=http://192.168.1.100,http://server.company.local,http://localhost
   ```
   Замените `192.168.1.100` на IP адрес вашего сервера.

### Шаг 3: Запуск развертывания

**Linux:**
```bash
# Используйте готовый скрипт
chmod +x deploy.sh
./deploy.sh build

# Или напрямую через docker-compose
docker-compose -f docker-compose.prod.yml up -d --build
```

**Windows (PowerShell):**
```powershell
docker-compose -f docker-compose.prod.yml up -d --build
```

### Шаг 4: Проверка статуса

```bash
docker-compose -f docker-compose.prod.yml ps
```

Все сервисы должны быть в статусе `Up`:
- `hh_analyzer_mongodb` - база данных
- `hh_analyzer_redis` - кэш и очередь задач
- `hh_analyzer_backend` - API сервер
- `hh_analyzer_celery` - обработчик фоновых задач
- `hh_analyzer_celery_beat` - планировщик задач
- `hh_analyzer_frontend` - веб-интерфейс

### Шаг 5: Проверка работы

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Должен вернуть: `{"status":"ok"}`

2. **Frontend:**
   Откройте в браузере: `http://SERVER_IP` (где SERVER_IP - IP адрес сервера)

3. **API Документация:**
   `http://SERVER_IP:8000/docs`

---

## 🔧 Настройка сети и Firewall

### Открытие портов

**Linux (ufw):**
```bash
sudo ufw allow 80/tcp    # Frontend (HTTP)
sudo ufw allow 8000/tcp # Backend API (если нужен внешний доступ)
```

**Windows (PowerShell):**
```powershell
New-NetFirewallRule -DisplayName "HH Analyzer HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HH Analyzer API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**Примечание:** Порт 8000 обычно используется только для внутреннего доступа. Frontend доступен на порту 80.

---

## 📝 Настройка переменных окружения

### Обязательные переменные:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `SECRET_KEY` | Секретный ключ для JWT (минимум 32 символа) | `your-secret-key-here` |
| `CORS_ORIGINS` | Разрешенные источники для CORS | `http://192.168.1.100,http://localhost` |
| `MONGODB_URL` | URL подключения к MongoDB | `mongodb://mongodb:27017` |
| `REDIS_URL` | URL подключения к Redis | `redis://redis:6379` |

### Опциональные переменные:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `ENVIRONMENT` | Окружение | `production` |
| `DEBUG` | Режим отладки | `false` |
| `CLOUDFLARE_WORKER_URL` | URL Cloudflare Worker для AI | Уже настроен |
| `RATE_LIMIT_PER_MINUTE` | Лимит запросов в минуту | `60` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

Полный список переменных см. в `env.production.template`.

---

## 🗄️ Использование внешних баз данных

### MongoDB

Если используете внешний MongoDB, измените в `.env`:
```
MONGODB_URL=mongodb://user:password@host:port/database
```

### Redis

Если используете внешний Redis, измените в `.env`:
```
REDIS_URL=redis://:password@host:port
```

**Важно:** При использовании внешних баз данных, удалите или закомментируйте сервисы `mongodb` и `redis` из `docker-compose.prod.yml`.

---

## 🔍 Мониторинг и логи

### Просмотр логов всех сервисов:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Логи конкретного сервиса:
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f mongodb
```

### Статус и использование ресурсов:
```bash
docker-compose -f docker-compose.prod.yml ps
docker stats
```

---

## 🔄 Управление сервисами

### Остановка:
```bash
docker-compose -f docker-compose.prod.yml down
```

### Перезапуск:
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Перезапуск конкретного сервиса:
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Обновление (после изменений в коде):
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 💾 Резервное копирование

### MongoDB Backup

**Автоматический скрипт (Linux):**
```bash
./scripts/backup_mongodb.sh
```

**Вручную:**
```bash
docker-compose -f docker-compose.prod.yml exec mongodb mongodump --out /data/backup/$(date +%Y%m%d_%H%M%S)
```

### Восстановление:
```bash
./scripts/restore_mongodb.sh /path/to/backup
```

---

## 🔐 Безопасность

### ✅ Чеклист безопасности:

- [ ] `SECRET_KEY` установлен и имеет минимум 32 символа
- [ ] `DEBUG=false` в production
- [ ] `CORS_ORIGINS` настроен только для разрешенных доменов
- [ ] `.env` файл не закоммичен в Git (проверьте `.gitignore`)
- [ ] Firewall настроен (открыты только необходимые порты)
- [ ] MongoDB и Redis защищены паролями (если доступны извне)
- [ ] Регулярные обновления Docker образов

---

## 🐛 Решение проблем

### Проблема: Контейнеры не запускаются

1. Проверьте логи:
   ```bash
   docker-compose -f docker-compose.prod.yml logs
   ```

2. Проверьте, что порты свободны:
   ```bash
   netstat -tuln | grep -E ':(80|8000|27017|6379)'
   ```

3. Проверьте файл `.env` на наличие всех обязательных переменных

### Проблема: Backend не отвечает

1. Проверьте логи backend:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   ```

2. Проверьте подключение к MongoDB:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python -c "from app.infrastructure.database import get_database; print('OK')"
   ```

### Проблема: Frontend не открывается

1. Проверьте логи frontend:
   ```bash
   docker-compose -f docker-compose.prod.yml logs frontend
   ```

2. Проверьте, что порт 80 открыт в firewall

3. Проверьте, что backend доступен:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

### Проблема: CORS ошибки

1. Убедитесь, что `CORS_ORIGINS` в `.env` содержит правильный адрес
2. Перезапустите backend:
   ```bash
   docker-compose -f docker-compose.prod.yml restart backend
   ```

---

## 📞 Контакты и поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте документацию в `README.md` и `PRODUCTION_CHECKLIST.md`

---

## 📚 Дополнительная документация

- `README.md` - Общее описание проекта
- `PRODUCTION_CHECKLIST.md` - Чеклист для production развертывания
- `env.production.template` - Шаблон переменных окружения
- `docker-compose.prod.yml` - Конфигурация Docker Compose

---

