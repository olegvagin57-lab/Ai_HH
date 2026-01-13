@echo off
echo Starting HH Resume Analyzer Backend...
cd backend
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause