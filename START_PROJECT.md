# Quick Start Guide - HH Resume Analyzer

## Prerequisites Check

1. **Check Python dependencies:**
   ```bash
   cd backend
   py -m scripts.check_setup
   ```

2. **Test connections:**
   ```bash
   cd backend
   py -m scripts.test_connection
   ```

## Starting the Project

### Option 1: Manual Start

1. **Start MongoDB:**
   ```bash
   mongod
   ```

2. **Start Redis (optional):**
   ```bash
   redis-server
   ```

3. **Start Backend:**
   ```bash
   cd backend
   py -m uvicorn app.main:app --reload --port 8000
   ```

4. **Start Celery Worker (in separate terminal):**
   ```bash
   cd backend
   celery -A celery_app.celery worker --loglevel=info
   ```

5. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Option 2: Docker Compose

```bash
docker-compose up -d
```

## Verify Installation

1. Backend API: http://localhost:8000
2. API Docs: http://localhost:8000/docs
3. Frontend: http://localhost:3000

## Create First User

Use the registration endpoint at `/api/v1/auth/register` or register via the frontend.

## Run Tests

```bash
# Full QA suite
py qa_test_suite.py

# Unit tests
cd backend
pytest tests/ -v
```
