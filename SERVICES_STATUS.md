# Services Status

## 🚀 Running Services

### Backend API
- **Status:** Starting/Running
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

### Frontend
- **Status:** ✅ Running
- **URL:** http://localhost:3000
- **Login:** http://localhost:3000/login

### Celery Worker
- **Status:** Starting (solo pool for Windows)
- **Note:** Will retry Redis connection when available

## 📝 Quick Access

1. **Open Frontend:** http://localhost:3000
2. **View API Docs:** http://localhost:8000/docs
3. **Check Health:** http://localhost:8000/health

## 🔧 Manual Start (if needed)

### Backend
```powershell
cd backend
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Celery Worker
```powershell
cd backend
py -m celery -A celery_app.celery worker --loglevel=info --pool=solo
```

### Frontend
```powershell
cd frontend
npm run dev
```

## ⚠️ Notes

- **Redis:** Not running (optional). Celery will work but may retry connections.
- **MongoDB:** Should be running for full functionality
- **Cloudflare Worker:** Returns 404, but fallback mode works

## 🎯 Next Steps

1. Open http://localhost:3000 in your browser
2. Register a new user
3. Create your first search
4. Explore the results!
