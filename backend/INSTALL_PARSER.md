# Установка parse_hh_data для работы без API ключей

Для работы с реальными данными HeadHunter без API ключей можно использовать библиотеку `parse_hh_data`.

## Установка

### Вариант 1: Установка из GitHub (рекомендуется)

```bash
pip install git+https://github.com/arinaaageeva/parse_hh_data.git
```

### Вариант 2: Установка в Docker

Добавьте в `backend/Dockerfile`:

```dockerfile
# Install parse_hh_data
RUN pip install git+https://github.com/arinaaageeva/parse_hh_data.git
```

Или добавьте в `docker-compose.yml` для backend сервиса:

```yaml
backend:
  # ... existing config ...
  command: >
    sh -c "pip install git+https://github.com/arinaaageeva/parse_hh_data.git && 
           uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

## Использование

После установки библиотека автоматически используется вместо mock данных, если:
- Нет настроенных HH API credentials (`HH_CLIENT_ID` и `HH_CLIENT_SECRET`)
- Библиотека `parse_hh_data` успешно установлена

## Особенности

1. **Парсинг резюме**: Библиотека скачивает обезличенные резюме с hh.ru в HTML формате и парсит их в JSON
2. **Поиск по ID**: Использует `download.resume_ids()` для получения списка ID резюме
3. **Фильтрация**: Применяет фильтрацию по запросу после получения данных
4. **Асинхронность**: Все операции выполняются в thread pool для избежания блокировки

## Ограничения

- Работает только с обезличенными резюме (без персональных данных)
- Может быть медленнее чем API (нужно скачивать и парсить HTML)
- Требует интернет-соединение для доступа к hh.ru
- Rate limits могут быть более строгими чем у API

## Пример использования

После установки просто создайте поиск через API:

```bash
POST /api/v1/search
{
  "query": "Python developer",
  "city": "Moscow"
}
```

Система автоматически использует парсер если нет API ключей.

## Документация parse_hh_data

- GitHub: https://github.com/arinaaageeva/parse_hh_data
- Использование: `from parse_hh_data import download, parse`
