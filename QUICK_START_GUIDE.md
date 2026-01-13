# Quick Start Guide - HH Resume Analyzer

## 🚀 Services Status

### Backend API
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Frontend
- **URL:** http://localhost:3000
- **Login Page:** http://localhost:3000/login

### Celery Worker
- Running in background for search processing

## 📝 First Steps

### 1. Register a New User

1. Open http://localhost:3000
2. Click "Sign up" or go to http://localhost:3000/register
3. Fill in the registration form:
   - Email: your@email.com
   - Username: yourusername
   - Password: (min 8 chars, uppercase, lowercase, digit)
   - Full Name, Company, Position (optional)

### 2. Login

1. Use your credentials to login
2. You'll be redirected to the search page

### 3. Create Your First Search

1. On the search page, enter:
   - **Query:** e.g., "Python developer with FastAPI experience"
   - **City:** e.g., "Москва"
2. Click "Start Search"
3. Wait for processing (you'll see status updates)

### 4. View Results

1. Once search completes, you'll see results
2. Results are sorted by AI score
3. Click "View" on any resume to see details
4. Export results to Excel or CSV

## 🔑 Default Admin User

To create an admin user, you can:

1. Register normally
2. Then update user in MongoDB:
   ```javascript
   db.users.updateOne(
     {email: "your@email.com"},
     {$set: {role_names: ["admin"]}}
   )
   ```

Or use the admin API endpoint (if you have admin access).

## 🛠️ Troubleshooting

### Backend not responding?
- Check if MongoDB is running: `mongod`
- Check backend logs for errors
- Verify port 8000 is not in use

### Frontend not loading?
- Check if npm dependencies are installed
- Verify port 3000 is not in use
- Check browser console for errors

### Search not processing?
- Check if Celery worker is running
- Check Redis connection (optional)
- Check backend logs for errors

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### Search
- `POST /api/v1/search` - Create new search
- `GET /api/v1/search` - List searches
- `GET /api/v1/search/{id}` - Get search details
- `GET /api/v1/search/{id}/resumes` - Get search results
- `GET /api/v1/search/{id}/export/excel` - Export to Excel
- `GET /api/v1/search/{id}/export/csv` - Export to CSV

### Users (Admin only)
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{id}` - Get user
- `PATCH /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

## 🎯 Next Steps

1. **Create searches** with different queries
2. **Explore results** and AI analysis
3. **Export data** for further analysis
4. **Manage users** (if admin)

Enjoy using HH Resume Analyzer! 🎉
