# Testing Checklist - HH Resume Analyzer

## Pre-Testing Setup

- [ ] Install backend dependencies: `pip install -r requirements.txt`
- [ ] Install frontend dependencies: `npm install`
- [ ] Configure `.env` file with proper settings
- [ ] Start MongoDB
- [ ] Start Redis (optional)
- [ ] Verify connections: `py -m scripts.test_connection`

## Backend Testing

### Unit Tests
- [ ] Run: `pytest backend/tests/ -v`
- [ ] All auth service tests pass
- [ ] All AI service tests pass
- [ ] All search service tests pass
- [ ] All API tests pass

### Integration Tests
- [ ] Run: `py qa_test_suite.py`
- [ ] Module imports test passes
- [ ] Configuration test passes
- [ ] Security functions test passes
- [ ] AI service test passes
- [ ] Database models test passes
- [ ] API structure test passes
- [ ] Error handling test passes

### Manual API Testing
- [ ] Start backend: `uvicorn app.main:app --reload`
- [ ] Access API docs: http://localhost:8000/docs
- [ ] Test POST /api/v1/auth/register
- [ ] Test POST /api/v1/auth/login
- [ ] Test GET /api/v1/auth/me (with token)
- [ ] Test POST /api/v1/search
- [ ] Test GET /api/v1/search/{id}
- [ ] Test GET /api/v1/search/{id}/resumes
- [ ] Test GET /api/v1/search/{id}/export/excel
- [ ] Test GET /health

## Frontend Testing

### Build Test
- [ ] Run: `npm run build`
- [ ] Build completes without errors

### Manual UI Testing
- [ ] Start frontend: `npm run dev`
- [ ] Access: http://localhost:3000
- [ ] Test registration page
- [ ] Test login page
- [ ] Test search page
- [ ] Test results page
- [ ] Test admin page (as admin user)
- [ ] Test protected routes
- [ ] Test logout functionality

## End-to-End Testing

### User Flow 1: Registration and Search
- [ ] Register new user
- [ ] Login with new user
- [ ] Create a search
- [ ] Wait for search to complete
- [ ] View results
- [ ] Export results

### User Flow 2: Admin Functions
- [ ] Login as admin
- [ ] View user list
- [ ] Edit user
- [ ] Delete user (if not self)

### User Flow 3: Search with AI Analysis
- [ ] Create search with complex query
- [ ] Verify concepts extracted
- [ ] Verify preliminary scoring
- [ ] Verify AI analysis for top resumes
- [ ] Check AI scores and summaries

## Performance Testing

- [ ] API response times < 500ms for simple requests
- [ ] Search creation responds immediately
- [ ] Background processing works correctly
- [ ] Frontend loads in < 3 seconds

## Security Testing

- [ ] Weak passwords rejected
- [ ] Invalid tokens rejected
- [ ] Unauthorized access blocked
- [ ] Rate limiting works (if enabled)
- [ ] CORS configured correctly

## Error Handling Testing

- [ ] Invalid input returns proper error
- [ ] Database errors handled gracefully
- [ ] External service failures use fallback
- [ ] Frontend shows error messages

## Final Verification

- [ ] All tests pass
- [ ] No critical errors in logs
- [ ] All features work as expected
- [ ] Documentation is complete
- [ ] Ready for deployment
