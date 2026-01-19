# Развертывание на локальном ПК для доступа из другого города

## 🎯 Варианты развертывания

У вас есть несколько вариантов, чтобы сделать сервис доступным из другого города:

### Вариант 1: Прямой доступ через интернет (требует настройки роутера)
### Вариант 2: Использование ngrok (самый простой)
### Вариант 3: Облачное развертывание (рекомендуется для production)

---

## 🚀 Вариант 1: Прямой доступ через интернет

### Требования:
- Статический IP адрес (или динамический с DDNS)
- Доступ к настройкам роутера
- Настройка firewall

### Шаг 1: Узнайте ваш внешний IP

```powershell
# Windows PowerShell
Invoke-RestMethod -Uri "https://api.ipify.org"
```

Или откройте в браузере: https://whatismyipaddress.com/

### Шаг 2: Настройте проброс портов на роутере

1. Откройте настройки роутера (обычно `192.168.1.1` или `192.168.0.1`)
2. Найдите раздел "Port Forwarding" или "Виртуальные серверы"
3. Добавьте правила:

| Внешний порт | Внутренний IP | Внутренний порт | Протокол |
|--------------|---------------|-----------------|----------|
| 80           | IP вашего ПК  | 3000            | TCP      |
| 8000         | IP вашего ПК  | 8000            | TCP      |

**Пример:**
- Внешний порт: `80` → Внутренний IP: `192.168.1.100` → Внутренний порт: `3000`
- Внешний порт: `8000` → Внутренний IP: `192.168.1.100` → Внутренний порт: `8000`

### Шаг 3: Настройте Windows Firewall

```powershell
# Откройте PowerShell от имени администратора

# Разрешить входящие подключения на порт 3000
New-NetFirewallRule -DisplayName "HH Analyzer Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow

# Разрешить входящие подключения на порт 8000
New-NetFirewallRule -DisplayName "HH Analyzer Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Шаг 4: Настройте CORS в `.env`

```env
# Узнайте ваш внешний IP и добавьте его в CORS_ORIGINS
CORS_ORIGINS=http://YOUR_EXTERNAL_IP,http://YOUR_EXTERNAL_IP:3000,http://localhost:3000

# Пример:
CORS_ORIGINS=http://123.45.67.89,http://123.45.67.89:3000,http://localhost:3000
```

### Шаг 5: Запустите проект

```powershell
# Используйте docker-compose для production
docker-compose -f docker-compose.prod.yml up -d --build
```

### Шаг 6: Проверьте доступность

Из другого города откройте в браузере:
```
http://YOUR_EXTERNAL_IP:3000
```

**⚠️ Проблемы:**
- Если у вас динамический IP, он может измениться. Используйте DDNS (DuckDNS, No-IP)
- Некоторые провайдеры блокируют входящие подключения на порт 80
- Может потребоваться настройка на стороне провайдера

---

## 🌐 Вариант 2: Использование ngrok (РЕКОМЕНДУЕТСЯ)

**Ngrok** создает безопасный туннель к вашему локальному серверу. Это самый простой способ.

### Шаг 1: Установите ngrok

1. Скачайте с https://ngrok.com/download
2. Распакуйте в папку (например, `C:\ngrok`)
3. Зарегистрируйтесь на https://dashboard.ngrok.com (бесплатно)
4. Получите токен авторизации

### Шаг 2: Настройте ngrok

```powershell
# Добавьте ngrok в PATH или используйте полный путь
cd C:\ngrok
.\ngrok.exe authtoken YOUR_AUTH_TOKEN
```

### Шаг 3: Запустите ngrok

```powershell
# Создайте туннель для фронтенда (порт 3000)
.\ngrok.exe http 3000

# Или для бэкенда (порт 8000)
.\ngrok.exe http 8000
```

Вы получите URL вида:
```
https://abc123.ngrok-free.app
```

### Шаг 4: Настройте CORS

```env
# Добавьте ngrok URL в CORS_ORIGINS
CORS_ORIGINS=https://abc123.ngrok-free.app,http://localhost:3000
```

### Шаг 5: Запустите проект

```powershell
# Запустите бэкенд и фронтенд
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# В другом терминале
cd frontend
npm run dev
```

### Шаг 6: Поделитесь URL

Отправьте ngrok URL пользователям из другого города:
```
https://abc123.ngrok-free.app
```

**⚠️ Ограничения бесплатного ngrok:**
- URL меняется при каждом перезапуске (если не используете платный план)
- Ограничение на количество подключений
- Может быть медленнее, чем прямой доступ

**💡 Решение:** Используйте ngrok с фиксированным доменом (платный план) или настройте скрипт для автоматического обновления URL.

---

## ☁️ Вариант 3: Облачное развертывание (для production)

### Рекомендуемые платформы:

1. **VPS (DigitalOcean, Linode, Hetzner)**
   - Полный контроль
   - Статический IP
   - От $5/месяц

2. **Heroku**
   - Простое развертывание
   - Бесплатный тариф (с ограничениями)
   - Автоматическое развертывание

3. **Railway / Render**
   - Простое развертывание
   - Бесплатный тариф
   - Автоматическое масштабирование

4. **AWS / Azure / GCP**
   - Для серьезных проектов
   - Много возможностей
   - Сложнее настройка

---

## 🔧 Настройка для локального развертывания

### 1. Обновите `.env` файл

```env
# Безопасность
SECRET_KEY=your-very-secure-secret-key-minimum-32-characters
ENVIRONMENT=production
DEBUG=false

# CORS - добавьте все возможные адреса
CORS_ORIGINS=http://YOUR_EXTERNAL_IP:3000,http://localhost:3000,https://your-ngrok-url.ngrok-free.app

# MongoDB и Redis (если используете Docker, оставьте как есть)
MONGODB_URL=mongodb://mongodb:27017
REDIS_URL=redis://redis:6379

# Hugging Face (уже настроен)
HUGGING_FACE_API_TOKEN=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
```

### 2. Генерация SECRET_KEY

```powershell
# PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 48 | ForEach-Object {[char]$_})
```

### 3. Запуск через Docker Compose

```powershell
# Соберите и запустите
docker-compose -f docker-compose.prod.yml up -d --build

# Проверьте статус
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Проверка работы

```powershell
# Проверьте health endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"

# Должен вернуть: {"status":"ok"}
```

---

## 🔐 Безопасность

### Обязательные меры:

1. **Измените SECRET_KEY** - не используйте значение по умолчанию
2. **Настройте CORS** - разрешите только нужные домены
3. **Используйте HTTPS** - настройте SSL сертификат (Let's Encrypt)
4. **Настройте firewall** - откройте только необходимые порты
5. **Используйте сильные пароли** - для пользователей системы

### Для ngrok:

Ngrok автоматически предоставляет HTTPS, что хорошо для безопасности.

---

## 📋 Чеклист развертывания

- [ ] Установлен Docker и Docker Compose
- [ ] Настроен `.env` файл с правильными значениями
- [ ] Сгенерирован SECRET_KEY
- [ ] Настроен CORS_ORIGINS
- [ ] Настроен firewall (Windows Firewall)
- [ ] Настроен проброс портов (если используете вариант 1)
- [ ] Установлен и настроен ngrok (если используете вариант 2)
- [ ] Проект запущен и доступен локально
- [ ] Проверена доступность извне
- [ ] Настроена безопасность

---

## 🐛 Решение проблем

### Проблема: Не могу подключиться из другого города

1. **Проверьте firewall:**
   ```powershell
   Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*HH*"}
   ```

2. **Проверьте, что порты открыты:**
   ```powershell
   netstat -ano | findstr ":3000"
   netstat -ano | findstr ":8000"
   ```

3. **Проверьте CORS настройки:**
   - Убедитесь, что внешний URL добавлен в `CORS_ORIGINS`
   - Перезапустите backend после изменения

### Проблема: CORS ошибки

1. Проверьте `.env` файл - `CORS_ORIGINS` должен содержать внешний URL
2. Перезапустите backend:
   ```powershell
   docker-compose -f docker-compose.prod.yml restart backend
   ```

### Проблема: ngrok URL не работает

1. Убедитесь, что ngrok запущен
2. Проверьте, что локальный сервер работает (`http://localhost:3000`)
3. Убедитесь, что ngrok URL добавлен в `CORS_ORIGINS`

---

## 💡 Рекомендации

### Для тестирования:
- Используйте **ngrok** - самый простой способ

### Для небольшой команды:
- Используйте **VPS** с фиксированным IP
- Настройте **DDNS** если IP динамический

### Для production:
- Используйте **облачное развертывание** (AWS, Azure, GCP)
- Настройте **домен** и **SSL сертификат**
- Используйте **CDN** для статики

---

## 📞 Дополнительная помощь

Если возникнут проблемы:
1. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs`
2. Проверьте документацию: `DEPLOYMENT_INSTRUCTIONS.md`
3. Проверьте настройки в `.env`
