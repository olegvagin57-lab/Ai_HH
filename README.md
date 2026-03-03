# HH Resume Analyzer

Сервис для поиска резюме на HeadHunter и первичной оценки кандидатов. Проект включает backend API, frontend (веб‑интерфейс) и фоновые задачи (Celery) для длительных операций: парсинг резюме, скоринг, генерация рекомендаций и т.п.

## Что умеет

- **Поиск резюме** по запросу и городу (HeadHunter).
- **Асинхронная обработка** поиска через Celery: прогресс, статусы, ошибки.
- **Скоринг** резюме: предварительный + итоговый (включая match % и детальные поля анализа).
- **ATS‑часть**: вакансии, кандидаты, статусы, теги/папки, сравнение, комментарии, уведомления, аналитика.
- **RBAC**: пользователи/роли/права.
- **Экспорт** результатов.

## Технологии

- **Backend**: FastAPI, Pydantic v2, Beanie (MongoDB), Redis, Celery, JWT.
- **Frontend**: React 18, MUI, React Router, React Query, Vite.

## Быстрый старт (Docker Compose)

1) Создай `.env` из шаблона:

```bash
cp env.production.template .env
```

2) Запусти сервисы:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

3) Проверки:
- **Frontend**: `http://localhost:3000`
- **Backend health**: `http://localhost:8000/api/v1/health/live`
- **API docs**: `http://localhost:8000/docs`

Подробная инструкция: `DEPLOYMENT_INSTRUCTIONS.md`.

## Локальный запуск (для разработки)

### Требования
- Python 3.11+
- Node.js 18+
- MongoDB + Redis (или Docker Compose)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows (PowerShell/CMD)
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Celery worker

```bash
cd backend
celery -A celery_app.celery worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Переменные окружения (минимум)

Фактические значения и полный список — в `env.production.template`.

- `MONGODB_URL` (например `mongodb://mongodb:27017` в Docker)
- `MONGODB_DATABASE` (по умолчанию `hh_analyzer`)
- `REDIS_URL` (например `redis://redis:6379` в Docker)
- `SECRET_KEY` (обязательно заменить для production)
- `CORS_ORIGINS` (например `http://localhost:3000,http://localhost`)
- `OLLAMA_URL` (по умолчанию `http://localhost:11434`)
- `OLLAMA_MODEL` (например `mistral`, `llama3`, `qwen2.5`)

## Архитектура (UML/диаграммы)

### Компоненты (Component)

```mermaid
flowchart LR
  User["User (Browser)"] --> Frontend["Frontend (React + Nginx)"]
  Frontend --> Backend["Backend API (FastAPI)"]

  Backend --> MongoDB[(MongoDB)]
  Backend --> Redis[(Redis)]

  Backend --> Celery["Celery Worker"]
  Celery --> Redis
  Celery --> MongoDB

  Celery --> HH["HeadHunter API"]
  Celery --> Ollama["Ollama (Local LLM)"]
```

### Флоу “Создать поиск резюме” (Sequence)

```mermaid
sequenceDiagram
  autonumber
  actor U as User
  participant FE as Frontend
  participant API as FastAPI
  participant DB as MongoDB
  participant Q as Celery
  participant HH as HeadHunter_API
  participant LLM as Ollama_Local

  U->>FE: Create_search(query, city)
  FE->>API: POST /api/v1/search
  API->>DB: Save Search(status=pending)
  API->>Q: enqueue process_search(search_id)
  API-->>FE: 201 SearchResponse

  Q->>DB: Update Search(status=processing)
  Q->>LLM: Extract concepts from query
  Q->>HH: Search resumes (paged)
  Q->>DB: Save Resume items + progress(processed_count)
  Q->>LLM: Analyze top resumes
  Q->>DB: Update resumes(ai_score, match %, details)
  Q->>DB: Update Search(status=completed)
  FE->>API: GET /api/v1/search/{id}/status
  API-->>FE: SearchResponse(status, progress)
```

### Упрощённая доменная модель (Class)

```mermaid
classDiagram
  class User {
    +string id
    +string email
    +string username
    +bool is_active
    +List~string~ role_names
  }
  class Role {
    +string name
    +List~string~ permission_names
  }
  class Permission {
    +string name
    +string display_name
  }

  class Search {
    +string id
    +string user_id
    +string query
    +string city
    +string status
    +int total_found
    +int processed_count
    +int total_to_process
  }
  class Concept {
    +string search_id
    +List~List~string~~ concepts
  }
  class Resume {
    +string id
    +string search_id
    +string hh_id
    +float preliminary_score
    +int ai_score
    +float match_percentage
    +bool analyzed
  }
  class Candidate {
    +string resume_id
    +string status
    +List~string~ tags
    +List~string~ vacancy_ids
  }
  class Vacancy {
    +string user_id
    +string title
    +string city
    +bool auto_matching_enabled
    +string auto_matching_frequency
    +List~string~ candidate_ids
  }
  class Interaction {
    +string resume_id
    +string user_id
    +string action_type
  }

  User "1" --> "many" Search : creates
  Search "1" --> "many" Resume : stores
  Search "1" --> "0..1" Concept : extracts
  Resume "1" --> "0..1" Candidate : extends
  Vacancy "many" --> "many" Candidate : associates
  Candidate "1" --> "many" Interaction : history
  User "many" --> "many" Role : has
  Role "many" --> "many" Permission : grants
```

## API (крупные группы эндпоинтов)

Backend монтируется с префиксом `/api/v1` и включает роуты:
- `/auth` (register/login/refresh/me/logout)
- `/users`
- `/search` (создание поиска, статусы, резюме, фильтры)
- `/export`
- `/candidates`
- `/vacancy`
- `/comments`
- `/comparison`
- `/notifications`
- `/analytics`
- `/bulk-actions`

## Структура проекта

```
HH_AI/
├── backend/     # FastAPI + Celery + доменная модель
├── frontend/    # React SPA
├── monitoring/  # Prometheus/Grafana/Loki configs
├── scripts/     # обслуживающие скрипты (backup, firewall, ngrok и т.д.)
└── docker-compose.prod.yml
```
