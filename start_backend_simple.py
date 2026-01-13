#!/usr/bin/env python3
"""
Простой запуск backend без установки зависимостей
"""

import os
import sys
import subprocess

def start_backend():
    """Запуск backend сервера"""
    print("🚀 Запуск HH Resume Analyzer Backend...")
    print("=" * 50)
    
    # Переходим в папку backend
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print("🌐 Сервер будет доступен на: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    print("-" * 50)
    
    try:
        # Запускаем uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
        
        print(f"🔧 Команда: {' '.join(cmd)}")
        print("⏳ Запуск сервера...")
        
        # Запускаем процесс
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Сервер остановлен пользователем")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_backend()