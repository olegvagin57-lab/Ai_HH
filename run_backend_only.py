#!/usr/bin/env python3
"""
Скрипт для запуска только backend API
Для тестирования через Swagger UI
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Запуск только backend"""
    print("🚀 Запуск Backend API...")
    print("=" * 50)
    
    # Проверяем, что мы в правильной директории
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Папка backend не найдена")
        return False
    
    # Проверяем requirements.txt
    requirements = backend_dir / "requirements.txt"
    if not requirements.exists():
        print("❌ requirements.txt не найден")
        return False
    
    try:
        # Запускаем backend
        print("🚀 Запуск FastAPI сервера...")
        print("📍 API будет доступен по адресу: http://localhost:8000")
        print("📍 Swagger UI: http://localhost:8000/docs")
        print("📍 ReDoc: http://localhost:8000/redoc")
        print("=" * 50)
        print("💡 Нажмите Ctrl+C для остановки")
        print()
        
        # Запуск uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=backend_dir, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска backend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Backend остановлен")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()