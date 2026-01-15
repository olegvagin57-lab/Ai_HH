# Доступ к приложению через Docker Toolbox

## ⚠️ Важно!

Docker Toolbox использует виртуальную машину VirtualBox. Порт **НЕ** пробрасывается на `localhost`, а на **IP-адрес Docker Machine**.

## 🔍 Определение IP-адреса Docker Machine

Выполните команду:
```powershell
docker-machine ip default
```

Обычно это: **192.168.99.100**

## 🌐 URL для доступа

Используйте IP Docker Machine вместо `localhost`:

- **Backend API**: http://192.168.99.100:8000
- **API Docs (Swagger)**: http://192.168.99.100:8000/docs
- **Frontend**: http://192.168.99.100:3000

## 🔧 Если порты не работают

### Настройка проброса портов в VirtualBox

1. **Откройте VirtualBox**
2. **Выберите машину `default`** (если она не запущена, запустите её)
3. **Настройки** → **Сеть** → **Адаптер 1**
4. **Тип подключения**: NAT
5. **Расширенные** → **Проброс портов**
6. **Добавьте следующие правила**:

#### Backend (порт 8000)
- **Имя**: backend
- **Протокол**: TCP
- **IP хоста**: 127.0.0.1
- **Порт хоста**: 8000
- **IP гостя**: (оставьте пустым)
- **Порт гостя**: 8000

#### Frontend (порт 3000)
- **Имя**: frontend
- **Протокол**: TCP
- **IP хоста**: 127.0.0.1
- **Порт хоста**: 3000
- **IP гостя**: (оставьте пустым)
- **Порт гостя**: 3000

7. **OK** для сохранения

### После настройки проброса портов

После настройки проброса портов в VirtualBox, вы сможете использовать:

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## ✅ Проверка доступности

### Проверка через PowerShell:

```powershell
# Проверка Backend
Invoke-WebRequest -Uri "http://192.168.99.100:8000/docs" -UseBasicParsing

# Проверка Frontend
Invoke-WebRequest -Uri "http://192.168.99.100:3000" -UseBasicParsing
```

### Проверка через браузер:

Просто откройте URL в браузере:
- http://192.168.99.100:8000/docs
- http://192.168.99.100:3000

## 🐛 Решение проблем

### Проблема: "Соединение отклонено" или таймаут

1. **Проверьте, что Docker Machine запущена**:
   ```powershell
   docker-machine status default
   ```
   Должно быть: `Running`

2. **Проверьте статус контейнеров**:
   ```powershell
   docker-compose ps
   ```
   Все контейнеры должны быть в статусе `Up`

3. **Проверьте логи**:
   ```powershell
   docker-compose logs backend
   docker-compose logs frontend
   ```

4. **Проверьте настройки файрвола Windows**:
   - Убедитесь, что порты 8000 и 3000 не заблокированы

### Проблема: "Страница не найдена" на Frontend

1. Проверьте логи frontend:
   ```powershell
   docker-compose logs frontend
   ```

2. Убедитесь, что frontend контейнер запущен:
   ```powershell
   docker-compose ps frontend
   ```

## 📝 Примечания

- IP-адрес Docker Machine может измениться после перезапуска. Всегда проверяйте его командой `docker-machine ip default`
- Если вы настроили проброс портов в VirtualBox, используйте `localhost`
- Если проброс портов не настроен, используйте IP Docker Machine (обычно 192.168.99.100)
