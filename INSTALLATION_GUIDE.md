# Installation and Testing Guide

## Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or if using Python launcher:
```bash
cd backend
py -m pip install -r requirements.txt
```

## Step 2: Verify Installation

```bash
cd backend
py -m scripts.check_setup
```

This will check if all required packages are installed.

## Step 3: Test Connections

```bash
cd backend
py -m scripts.test_connection
```

This will test:
- MongoDB connection
- Redis connection (optional)
- Cloudflare Worker connection (with fallback)

## Step 4: Run QA Test Suite

```bash
py qa_test_suite.py
```

This comprehensive test suite will verify:
- Module imports
- Configuration
- Security functions
- AI service
- Database models
- API structure
- Error handling

## Step 5: Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Step 6: Start Services

### Backend
```bash
cd backend
py -m uvicorn app.main:app --reload --port 8000
```

### Celery Worker (separate terminal)
```bash
cd backend
celery -A celery_app.celery worker --loglevel=info
```

### Frontend
```bash
cd frontend
npm run dev
```

## Step 7: Verify Everything Works

1. Open http://localhost:8000/docs - Should see API documentation
2. Open http://localhost:3000 - Should see login page
3. Register a new user
4. Create a search
5. View results

## Troubleshooting

### MongoDB Connection Failed
- Ensure MongoDB is running: `mongod`
- Check connection string in `.env` file

### Redis Connection Failed
- Redis is optional for rate limiting
- System will use in-memory rate limiting if Redis is unavailable

### Cloudflare Worker Failed
- System will use fallback mode for AI analysis
- Check `CLOUDFLARE_WORKER_URL` in `.env`

### Import Errors
- Run `pip install -r requirements.txt` again
- Check Python version (3.11+ required)
