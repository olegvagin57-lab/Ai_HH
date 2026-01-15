# Инструкция по запуску тестов

## Быстрый старт

### Backend тесты

```bash
cd backend

# Установить зависимости (если еще не установлены)
pip install -r requirements.txt

# Запустить все тесты
pytest

# Запустить с coverage отчетом
pytest --cov=app --cov-report=html

# Просмотреть coverage отчет
# Откроется в браузере: backend/htmlcov/index.html
```

### Frontend тесты

```bash
cd frontend

# Установить зависимости (если еще не установлены)
npm install

# Запустить компонентные тесты
npm test

# Запустить с coverage
npm run test:coverage

# Запустить E2E тесты (требует запущенного приложения)
npm run test:e2e
```

## Запуск конкретных категорий тестов

### Backend

```bash
# Только unit тесты
pytest tests/services/ tests/domain/ tests/infrastructure/

# Только integration тесты
pytest tests/integration/

# Только security тесты
pytest tests/security/

# Только performance тесты
pytest tests/performance/

# Только Celery tasks тесты
pytest tests/tasks/

# По маркерам
pytest -m unit
pytest -m integration
pytest -m security
pytest -m performance
```

### Frontend

```bash
# Конкретный тест
npm test -- LoginPage.test.jsx

# E2E конкретный сценарий
npm run test:e2e -- auth.spec.js
```

## Проверка покрытия

### Backend

```bash
cd backend
pytest --cov=app --cov-report=term-missing

# HTML отчет
pytest --cov=app --cov-report=html
# Откроется: backend/htmlcov/index.html
```

### Frontend

```bash
cd frontend
npm run test:coverage

# Отчет будет в: frontend/coverage/
```

## Отладка тестов

### Backend

```bash
# С подробным выводом
pytest -v

# С выводом print statements
pytest -s

# Остановка на первой ошибке
pytest -x

# Запуск с отладчиком
pytest --pdb
```

### Frontend

```bash
# В watch режиме
npm run test:watch

# С отладкой
npm test -- --debug
```

## Требования

### Backend
- Python 3.11+
- MongoDB (для тестов используется тестовая БД)
- Redis (опционально, для некоторых тестов)

### Frontend
- Node.js 18+
- Браузеры для E2E тестов (устанавливаются автоматически Playwright)

## Примечания

1. Тесты используют отдельную тестовую БД (`hh_analyzer_test`)
2. Тестовая БД автоматически очищается после тестов
3. E2E тесты требуют запущенного приложения (автоматически запускается через Playwright)
4. Некоторые тесты используют моки для внешних сервисов

## Решение проблем

### Ошибки подключения к БД
- Убедитесь, что MongoDB запущен
- Проверьте MONGODB_URL в настройках

### Ошибки импорта
- Убедитесь, что все зависимости установлены
- Проверьте PYTHONPATH

### Ошибки в async тестах
- Убедитесь, что используется `@pytest.mark.asyncio`
- Проверьте версию pytest-asyncio
