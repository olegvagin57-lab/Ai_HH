# Решение проблемы с памятью в Docker Toolbox

## Проблема
При сборке backend образа возникает ошибка:
```
lzma error: Cannot allocate memory
```

Это происходит из-за нехватки памяти в виртуальной машине Docker Toolbox.

## Решения

### Вариант 1: Увеличить память Docker Machine (РЕКОМЕНДУЕТСЯ)

1. Остановить Docker Machine:
```powershell
docker-machine stop default
```

2. Увеличить память через VirtualBox:
   - Откройте VirtualBox Manager
   - Найдите машину "default"
   - Правый клик → Settings → System → Motherboard
   - Увеличьте Base Memory до **4096 MB** (4 GB) или больше
   - Сохраните и закройте

3. Запустить Docker Machine:
```powershell
docker-machine start default
docker-machine env default | Invoke-Expression
```

### Вариант 2: Упростить Dockerfile (быстрое решение)

Убрать gcc и git, если они не критичны для проекта. Многие Python пакеты имеют предкомпилированные wheels.

### Вариант 3: Использовать более легкий базовый образ

Использовать `python:3.11-alpine` вместо `python:3.11-slim` - он занимает меньше места.

## Текущая ситуация

- Docker Machine по умолчанию имеет **1024 MB** памяти
- Сборка с gcc требует **минимум 2-3 GB**
- Рекомендуется **4 GB** для комфортной работы

## Проверка после исправления

```powershell
docker-machine inspect default --format "{{.Driver.Memory}}"
```

Должно показать 4096 или больше.
