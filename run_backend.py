#!/usr/bin/env python3
"""
Simple backend runner for development without Docker
"""

import sys
import os
import subprocess

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def install_requirements():
    """Install required packages"""
    requirements = [
        'fastapi==0.104.1',
        'uvicorn[standard]==0.24.0',
        'sqlalchemy==2.0.23',
        'python-multipart==0.0.6',
        'pydantic==2.5.0',
        'pydantic-settings==2.1.0',
        'python-dotenv==1.0.0',
        'beautifulsoup4==4.12.2',
        'requests==2.31.0'
    ]
    
    print("📦 Installing required packages...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {req}, continuing...")

def run_server():
    """Run the FastAPI server"""
    print("🚀 Starting HH Resume Analyzer Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    os.chdir('backend')
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    install_requirements()
    run_server()