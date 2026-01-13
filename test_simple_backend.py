#!/usr/bin/env python3
"""
Простой тест backend без сложных зависимостей
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Создаем простое приложение
app = FastAPI(
    title="HH Resume Analyzer - Simple Test",
    description="Простой тест backend API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HH Resume Analyzer Backend is running!"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "hh-resume-analyzer",
        "version": "1.0.0"
    }

@app.get("/api/v1/test")
async def test_api():
    return {
        "message": "API is working!",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/test",
            "/docs"
        ]
    }

if __name__ == "__main__":
    print("Starting simple backend...")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )