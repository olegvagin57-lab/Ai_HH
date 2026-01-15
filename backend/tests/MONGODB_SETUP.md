# Настройка MongoDB для тестов

## Быстрый старт

### Вариант 1: Использование скриптов (рекомендуется)

1. **Запуск MongoDB:**
   ```powershell
   cd backend/scripts
   .\start_mongodb_test.ps1
   ```

2. **Запуск тестов с автоматическим управлением MongoDB:**
   ```powershell
   cd backend/scripts
   .\run_tests_with_mongodb.ps1
   ```

3. **Остановка MongoDB:**
   ```powershell
   cd backend/scripts
   .\stop_mongodb_test.ps1
   ```

### Вариант 2: Ручное управление через Docker

1. **Запуск MongoDB:**
   ```powershell
   # Из корневой директории проекта
   docker-compose up -d mongodb
   ```

2. **Проверка статуса:**
   ```powershell
   docker ps --filter "name=hh_analyzer_mongodb"
   ```

3. **Проверка подключения:**
   ```powershell
   docker exec hh_analyzer_mongodb mongosh --eval "db.adminCommand('ping')"
   ```

4. **Запуск тестов:**
   ```powershell
   cd backend
   python -m pytest tests/ -v
   ```

5. **Остановка MongoDB:**
   ```powershell
   docker-compose stop mongodb
   # или
   docker stop hh_analyzer_mongodb
   ```

## Проверка подключения

### Проверка через Python

```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command('ping')
        print("✓ MongoDB подключен успешно")
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
    finally:
        client.close()

asyncio.run(test_connection())
```

### Проверка через командную строку

```powershell
# Проверка порта
Test-NetConnection -ComputerName localhost -Port 27017

# Проверка через docker
docker exec hh_analyzer_mongodb mongosh --eval "db.adminCommand('ping')"
```

## Настройка подключения

По умолчанию тесты используют настройки из `app/config.py`:
- URL: `mongodb://localhost:27017`
- Database: `hh_analyzer_test` (добавляется суффикс `_test`)

Для изменения настроек отредактируйте переменные окружения или `app/config.py`.

## Устранение проблем

### MongoDB не запускается

1. Проверьте, не занят ли порт 27017:
   ```powershell
   netstat -ano | findstr :27017
   ```

2. Проверьте логи контейнера:
   ```powershell
   docker logs hh_analyzer_mongodb
   ```

3. Пересоздайте контейнер:
   ```powershell
   docker-compose down mongodb
   docker-compose up -d mongodb
   ```

### Ошибки подключения в тестах

1. Убедитесь, что MongoDB запущен:
   ```powershell
   docker ps --filter "name=hh_analyzer_mongodb"
   ```

2. Проверьте, что порт 27017 доступен:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 27017
   ```

3. Проверьте настройки подключения в `app/config.py`

### Тесты пропускаются (skipped)

Если тесты пропускаются с сообщением о недоступности MongoDB:
- Запустите MongoDB через один из способов выше
- Убедитесь, что подключение работает (см. раздел "Проверка подключения")

## Автоматизация в CI/CD

Для автоматизации в CI/CD можно использовать:

```yaml
# Пример для GitHub Actions
services:
  mongodb:
    image: mongo:5.0
    ports:
      - 27017:27017
    options: >-
      --health-cmd "mongosh --eval 'db.adminCommand(\"ping\")'"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Дополнительная информация

- MongoDB версия: 5.0 (из docker-compose.yml)
- Контейнер: `hh_analyzer_mongodb`
- Порт: `27017`
- Тестовая база данных: `{MONGODB_DATABASE}_test`
