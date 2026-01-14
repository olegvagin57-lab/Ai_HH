# Инструкция по запуску проекта

## ✅ Что уже сделано

1. ✅ Python зависимости установлены
2. ✅ Frontend зависимости установлены  
3. ✅ Backend и Frontend запущены в фоне

## ⚠️ Что нужно сделать вручную

### 1. Создайте файл `.env` в папке `backend/`

Создайте файл `backend/.env` со следующим содержимым:

```env
ENVIRONMENT=development
DEBUG=true
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=hh_analyzer
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-required-12345678901234567890
CLOUDFLARE_WORKER_URL=https://proud-water-5293.olegvagin1311.workers.dev
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
```

**ВАЖНО:** Замените `SECRET_KEY` на случайную строку минимум 32 символа! Можно использовать:
- Онлайн генератор: https://www.random.org/strings/
- Или команду: `py -c "import secrets; print(secrets.token_urlsafe(32))"`

### 2. Установите MongoDB

**Вариант A: MongoDB Atlas (рекомендуется, бесплатно)**
1. Зарегистрируйтесь: https://www.mongodb.com/cloud/atlas
2. Создайте бесплатный кластер
3. Получите connection string
4. Замените `MONGODB_URL` в `.env` на ваш connection string

**Вариант B: Локальная установка**
1. Скачайте: https://www.mongodb.com/try/download/community
2. Установите MongoDB
3. Запустите (обычно запускается автоматически)

### 3. Redis (опционально)

Redis нужен для Celery и rate limiting, но приложение будет работать и без него.

Если не устанавливаете Redis - просто закомментируйте или удалите строку `REDIS_URL` из `.env`.

## 🚀 Запуск проекта

### Если процессы уже запущены

Backend должен быть доступен на: http://localhost:8000
Frontend должен быть доступен на: http://localhost:3000

### Если нужно перезапустить

**Терминал 1 - Backend:**
```bash
cd backend
py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Терминал 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Терминал 3 - Celery Worker (опционально, если Redis установлен):**
```bash
cd backend
celery -A celery_app.celery worker --loglevel=info
```

**Терминал 4 - Celery Beat (опционально, для автоматического подбора):**
```bash
cd backend
celery -A celery_app.celery beat --loglevel=info
```

## 📋 Проверка работы

1. Откройте http://localhost:3000 в браузере
2. Должна открыться страница входа
3. Зарегистрируйте нового пользователя
4. Войдите в систему
5. Создайте первый поиск резюме

## 🔍 Проверка API

- Backend API: http://localhost:8000/docs (Swagger документация)
- Health check: http://localhost:8000/api/v1/health

## ❗ Возможные проблемы

### Backend не запускается
- Проверьте, что MongoDB запущен
- Проверьте `.env` файл (особенно `SECRET_KEY`)
- Проверьте логи в консоли

### Frontend не подключается к Backend
- Убедитесь, что backend запущен на порту 8000
- Проверьте `vite.config.js` - proxy должен быть настроен на `http://localhost:8000`

### MongoDB не подключается
- Проверьте, что MongoDB запущен
- Проверьте `MONGODB_URL` в `.env`
- Для MongoDB Atlas: проверьте IP whitelist

### Redis ошибки
- Это нормально! Приложение работает без Redis
- Просто закомментируйте `REDIS_URL` в `.env`

## 📝 Логи

Логи backend будут отображаться в терминале, где запущен `uvicorn`.
Логи frontend будут отображаться в терминале, где запущен `npm run dev`.
