#!/usr/bin/env python3
"""
Run simple version of HH Resume Analyzer for demo
"""

import sys
import os
import subprocess
import webbrowser
import time

def install_basic_requirements():
    """Install minimal required packages"""
    requirements = [
        'fastapi',
        'uvicorn[standard]',
        'pydantic'
    ]
    
    print("📦 Installing minimal packages...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {req}")

def run_backend():
    """Run the simple backend"""
    print("🚀 Starting HH Resume Analyzer (Demo Mode)")
    print("📍 Backend: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    # Change to backend directory
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_path)
    
    try:
        # Run the simple version
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main_simple:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    print("🎯 HH Resume Analyzer - Simple Demo")
    print("=" * 50)
    print("This demo version uses mock data to show functionality")
    print("For full functionality, you need:")
    print("- HH.ru API keys")
    print("- Gemini API key (working in supported regions)")
    print("- Docker or full Python environment")
    print("=" * 50)
    print()
    
    install_basic_requirements()
    
    print("💡 After backend starts:")
    print("1. Open http://localhost:8000/docs to see API")
    print("2. Test search endpoint with city and query")
    print("3. Check results with mock data")
    print()
    
    run_backend()

if __name__ == "__main__":
    main()