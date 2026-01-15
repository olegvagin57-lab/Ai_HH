# Backend Tests

## Структура тестов

- `services/` - Unit тесты для сервисов
- `domain/` - Тесты domain entities
- `infrastructure/` - Тесты infrastructure слоя
- `integration/` - Integration тесты для API
- `tasks/` - Тесты Celery задач
- `security/` - Тесты безопасности
- `performance/` - Тесты производительности
- `edge_cases/` - Тесты граничных случаев

## Запуск тестов

```bash
# Все тесты
pytest

# С coverage
pytest --cov=app --cov-report=html

# Конкретная категория
pytest tests/services/          # Unit тесты
pytest tests/integration/       # Integration тесты
pytest tests/security/          # Security тесты

# По маркерам
pytest -m unit
pytest -m integration
pytest -m security
```

## Фикстуры

Доступные фикстуры в `conftest.py`:
- `test_user` - обычный пользователь
- `admin_user` - администратор
- `hr_manager_user` - HR менеджер
- `hr_specialist_user` - HR специалист
- `test_search` - тестовый поиск
- `test_resume` - тестовое резюме
- `test_vacancy` - тестовая вакансия
- `test_candidate` - тестовый кандидат
