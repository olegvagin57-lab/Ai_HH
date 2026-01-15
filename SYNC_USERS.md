# Синхронизация пользователей между ПК

Есть несколько способов синхронизировать аккаунты пользователей между разными компьютерами.

## Способ 1: Экспорт/импорт через скрипты (Рекомендуется)

### На первом ПК (где есть аккаунты):

1. **Экспорт пользователей:**
```bash
# В контейнере backend
docker-compose exec backend python scripts/export_users.py -o users_export.json

# Или если запущено локально
cd backend
python scripts/export_users.py -o users_export.json
```

2. **Скопируйте файл `users_export.json`** на второй ПК (через USB, сеть, облако и т.д.)

### На втором ПК (где нужно импортировать):

1. **Поместите файл `users_export.json`** в папку `backend/`

2. **Импорт пользователей:**
```bash
# В контейнере backend
docker-compose exec backend python scripts/import_users.py users_export.json

# Или если запущено локально
cd backend
python scripts/import_users.py users_export.json
```

**Опции импорта:**
- По умолчанию: существующие пользователи пропускаются (не перезаписываются)
- `--overwrite`: перезаписать существующих пользователей

```bash
# Перезаписать существующих пользователей
docker-compose exec backend python scripts/import_users.py users_export.json --overwrite
```

---

## Способ 2: Полный экспорт/импорт MongoDB (mongodump/mongorestore)

Этот способ экспортирует всю базу данных, включая все данные (пользователи, поиски, резюме и т.д.).

### На первом ПК:

1. **Экспорт всей базы данных:**
```bash
# Экспорт в папку backup
docker-compose exec mongodb mongodump --db hh_analyzer --out /data/backup

# Копирование из контейнера
docker cp hh_analyzer_mongodb:/data/backup ./mongodb_backup
```

### На втором ПК:

1. **Копируйте папку `mongodb_backup`** на второй ПК

2. **Импорт базы данных:**
```bash
# Копирование в контейнер
docker cp ./mongodb_backup hh_analyzer_mongodb:/data/backup

# Импорт
docker-compose exec mongodb mongorestore --db hh_analyzer /data/backup/hh_analyzer
```

---

## Способ 3: Использование общей MongoDB (удаленной)

Если у вас есть доступ к удаленной MongoDB (MongoDB Atlas, облачный сервер и т.д.), можно настроить оба ПК на использование одной базы данных.

### Настройка:

1. **Измените `docker-compose.yml`** или создайте `.env` файл:

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - MONGODB_URL=mongodb://your-remote-mongodb-url:27017
      - MONGODB_DATABASE=hh_analyzer
```

Или через `.env`:
```env
MONGODB_URL=mongodb://your-remote-mongodb-url:27017
MONGODB_DATABASE=hh_analyzer
```

2. **Перезапустите контейнеры:**
```bash
docker-compose down
docker-compose up -d
```

---

## Способ 4: Ручной экспорт через MongoDB Compass

Если у вас установлен MongoDB Compass:

1. **На первом ПК:**
   - Откройте MongoDB Compass
   - Подключитесь к базе данных
   - Выберите коллекцию `users`
   - Export Collection → JSON
   - Сохраните файл

2. **На втором ПК:**
   - Откройте MongoDB Compass
   - Подключитесь к базе данных
   - Выберите коллекцию `users`
   - Import Collection → выберите JSON файл

---

## Рекомендации

- **Для разработки:** Используйте Способ 1 (скрипты экспорта/импорта) - он простой и безопасный
- **Для полной синхронизации:** Используйте Способ 2 (mongodump/mongorestore)
- **Для постоянной синхронизации:** Используйте Способ 3 (общая MongoDB)

## Важные замечания

⚠️ **Безопасность:**
- Файлы экспорта содержат хеши паролей - храните их в безопасности
- Не коммитьте файлы экспорта в Git

⚠️ **Конфликты:**
- При импорте существующие пользователи по умолчанию пропускаются
- Используйте `--overwrite` только если уверены, что хотите перезаписать данные
