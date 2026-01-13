#!/usr/bin/env python3
"""
Запуск полного backend с минимальными зависимостями
"""

import os
import sys
import subprocess

def install_minimal_deps():
    """Установка только критически необходимых зависимостей"""
    print("📦 Установка критических зависимостей...")
    
    # Только самые необходимые пакеты
    critical_packages = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0", 
        "motor>=3.3.2",
        "pymongo>=4.6.0",
        "python-multipart>=0.0.6",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "httpx>=0.25.2",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "aiofiles>=23.2.1",
        "beanie>=1.23.6"
    ]
    
    for package in critical_packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Пропускаем {package}: {e}")
            continue

def start_backend():
    """Запуск полного backend"""
    print("🚀 Запуск HH Resume Analyzer Backend (Полная версия)...")
    print("=" * 60)
    
    # Устанавливаем критические зависимости
    install_minimal_deps()
    
    # Переходим в папку backend
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    print(f"📁 Рабочая директория: {backend_dir}")
    print("🌐 Сервер будет доступен на: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    print("🔗 Cloudflare Worker: https://proud-water-5293.olegvagin1311.workers.dev")
    print("-" * 60)
    
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
        print("⏳ Запуск полного backend...")
        
        # Запускаем процесс в папке backend
        subprocess.run(cmd, cwd=backend_dir, check=True)
        
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