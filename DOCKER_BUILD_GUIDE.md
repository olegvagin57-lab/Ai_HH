# Руководство по сборке Docker с мониторингом прогресса

## Быстрый старт

### Вариант 1: Использование скрипта (рекомендуется)

```powershell
# Сборка с мониторингом в реальном времени
.\docker-build.ps1 -Watch

# Обычная сборка с подробными логами
.\docker-build.ps1
```

### Вариант 2: Прямой запуск через docker-compose

```powershell
# Настройка окружения
$env:PATH += ";C:\Program Files\Docker Toolbox"
docker-machine env default | Invoke-Expression

# Сборка с подробными логами
docker-compose build --progress=plain

# Или сборка конкретного сервиса
docker-compose build --progress=plain backend
docker-compose build --progress=plain frontend
```

## Просмотр логов

### Просмотр логов всех контейнеров
```powershell
.\docker-logs.ps1
```

### Просмотр логов конкретного сервиса
```powershell
.\docker-logs.ps1 -Service backend
.\docker-logs.ps1 -Service frontend
.\docker-logs.ps1 -Service mongodb
```

### Просмотр последних 100 строк без обновления
```powershell
.\docker-logs.ps1 -Follow:$false
```

## Что улучшено

### Backend Dockerfile
- ✅ Добавлен прогресс-бар для pip (`--progress-bar=pretty`)
- ✅ Подробный вывод при установке зависимостей

### Frontend Dockerfile
- ✅ Добавлен прогресс для npm (`--progress=true --loglevel=info`)
- ✅ Подробный вывод при сборке

### Скрипты мониторинга
- ✅ `docker-build.ps1` - сборка с цветным выводом и мониторингом
- ✅ `docker-logs.ps1` - просмотр логов контейнеров

## Цветовая индикация в логах

- 🟢 **Зеленый** - шаги сборки (Step X/Y)
- 🟡 **Желтый** - установка/загрузка пакетов
- 🔴 **Красный** - ошибки

## Полезные команды

```powershell
# Проверка статуса контейнеров
docker-compose ps

# Просмотр логов конкретного контейнера
docker-compose logs -f backend

# Пересборка без кэша
docker-compose build --no-cache --progress=plain

# Остановка всех контейнеров
docker-compose down

# Запуск всех контейнеров
docker-compose up -d

# Перезапуск конкретного сервиса
docker-compose restart backend
```

## Решение проблем

### Если сборка зависла
1. Проверьте логи: `docker-compose logs`
2. Проверьте использование ресурсов: `docker stats`
3. Перезапустите Docker Machine: `docker-machine restart default`

### Если не хватает места
```powershell
# Очистка неиспользуемых образов
docker system prune -a

# Очистка только остановленных контейнеров
docker container prune
```

### Если нужно пересобрать с нуля
```powershell
docker-compose down -v
docker-compose build --no-cache --progress=plain
docker-compose up -d
```
