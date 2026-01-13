# HH Resume Analyzer

AI-powered resume analysis system for HeadHunter with Gemini integration.

## Features

- **Resume Search**: Search resumes from HeadHunter by city and job description
- **AI Analysis**: Deep AI analysis of top candidates using Gemini API
- **Concept Extraction**: Automatic extraction of key concepts from job descriptions
- **Scoring System**: Preliminary scoring and AI-based scoring (1-10 scale)
- **Export**: Export results to Excel/CSV
- **User Management**: Role-based access control (Admin, HR Manager, HR Specialist, Viewer)
- **Real-time Updates**: Polling-based status updates for search processing

## Tech Stack

### Backend
- **FastAPI** 0.104+ - Modern Python web framework
- **MongoDB** 7+ with **Beanie** ODM
- **Redis** 7+ - Caching and Celery broker
- **Celery** - Background task processing
- **Pydantic** v2 - Data validation
- **JWT** - Authentication

### Frontend
- **React** 18+ with JavaScript
- **Material-UI** v5 - UI components
- **React Query** - Data fetching and caching
- **React Router** v6 - Routing
- **Vite** - Build tool

## Project Structure

```
HH_AI/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes and schemas
│   │   ├── application/      # Business logic services
│   │   ├── core/             # Core utilities (security, logging, etc.)
│   │   ├── domain/           # Domain entities
│   │   ├── infrastructure/   # External services, database
│   │   └── main.py          # FastAPI app entry point
│   ├── celery_app/          # Celery configuration and tasks
│   └── tests/               # Tests
├── frontend/
│   └── src/
│       ├── api/             # API client
│       ├── features/        # Feature-based modules
│       ├── shared/          # Shared components
│       └── app/             # App configuration
└── .kiro/specs/            # Project specifications
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB 7+
- Redis 7+

### Installation

1. **Clone the repository**

2. **Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**

```bash
cd frontend
npm install
```

4. **Environment Variables**

Create `.env` file in the root directory:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=hh_analyzer

# Redis
REDIS_URL=redis://localhost:6379

# Cloudflare Worker (Gemini proxy)
CLOUDFLARE_WORKER_URL=https://proud-water-5293.olegvagin1311.workers.dev

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Running Locally

1. **Start MongoDB and Redis**

```bash
# MongoDB
mongod

# Redis
redis-server
```

2. **Start Backend**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

3. **Start Celery Worker**

```bash
cd backend
celery -A celery_app.celery worker --loglevel=info
```

4. **Start Frontend**

```bash
cd frontend
npm run dev
```

### Running with Docker

```bash
docker-compose up -d
```

This will start:
- MongoDB on port 27017
- Redis on port 6379
- Backend API on port 8000
- Celery worker
- Frontend on port 3000

## API Documentation

Once the backend is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Credentials

After first run, create a user via the registration endpoint or directly in MongoDB.

To create an admin user programmatically:

```python
from app.application.services.auth_service import AuthService
from app.domain.entities.user import User

auth_service = AuthService()
user = await auth_service.register_user(
    email="admin@example.com",
    username="admin",
    password="SecurePassword123",
    role_names=["admin"]
)
```

## Architecture

### Clean Architecture

The project follows Clean Architecture principles:

- **Domain Layer**: Entities and value objects (business logic)
- **Application Layer**: Use cases and services (orchestration)
- **Infrastructure Layer**: External services, database, cache
- **API Layer**: HTTP endpoints, request/response models

### Background Processing

Search processing is handled asynchronously:

1. User creates search → Search record created with "pending" status
2. Celery task `process_search_task` triggered
3. Task fetches resumes from HeadHunter
4. Preliminary scoring applied to all resumes
5. Top 50 resumes selected for deep AI analysis
6. AI analysis performed via Cloudflare Worker
7. Search status updated to "completed"

### Circuit Breaker

The Cloudflare Worker client implements a circuit breaker pattern:
- **CLOSED**: Normal operation
- **OPEN**: Service failing, requests rejected
- **HALF_OPEN**: Testing if service recovered

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Production Deployment

1. Update environment variables for production
2. Set `ENVIRONMENT=production` and `DEBUG=false`
3. Change `SECRET_KEY` to a secure random value
4. Configure proper CORS origins
5. Set up SSL/TLS certificates
6. Use production-grade MongoDB and Redis instances
7. Configure proper logging and monitoring

## License

MIT
