#!/usr/bin/env python3
"""
Простой скрипт для запуска системы HH Resume Analyzer
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    """Запуск системы"""
    print("🎯 HH Resume Analyzer - Запуск системы")
    print("=" * 50)
    
    # Проверяем зависимости
    backend_dir = Path("backend")
    frontend_dir = Path("frontend")
    
    if not backend_dir.exists():
        print("❌ Папка backend не найдена")
        return False
    
    if not frontend_dir.exists():
        print("❌ Папка frontend не найдена")
        return False
    
    # Проверяем node_modules
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Установка frontend зависимостей...")
        try:
            subprocess.run([
                "cmd", "/c", "cd frontend && npm install"
            ], check=True)
            print("✅ Frontend зависимости установлены")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки frontend зависимостей: {e}")
            return False
    
    print("\n🚀 Запуск сервисов...")
    print("📍 Backend API: http://localhost:8000")
    print("📍 Frontend App: http://localhost:3000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    # Запуск backend
    print("🚀 Запуск Backend...")
    try:
        backend_process = subprocess.Popen([
            "cmd", "/c", "cd backend && py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
        ], shell=True)
        print("✅ Backend запущен (PID: {})".format(backend_process.pid))
    except Exception as e:
        print(f"❌ Ошибка запуска backend: {e}")
        return False
    
    # Ждем запуска backend
    print("⏳ Ожидание запуска backend...")
    time.sleep(3)
    
    # Запуск frontend
    print("🚀 Запуск Frontend...")
    try:
        frontend_process = subprocess.Popen([
            "cmd", "/c", "cd frontend && npm start"
        ], shell=True)
        print("✅ Frontend запущен (PID: {})".format(frontend_process.pid))
    except Exception as e:
        print(f"❌ Ошибка запуска frontend: {e}")
        backend_process.terminate()
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Система запущена!")
    print("💡 Откройте браузер и перейдите по адресу:")
    print("   👉 http://localhost:3000 - Frontend приложение")
    print("   👉 http://localhost:8000/docs - API документация")
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        # Ожидание завершения
        while True:
            time.sleep(1)
            
            # Проверяем, что процессы еще работают
            if backend_process.poll() is not None:
                print("⚠️  Backend завершился")
                break
            
            if frontend_process.poll() is not None:
                print("⚠️  Frontend завершился")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
    
    finally:
        # Остановка процессов
        print("🛑 Остановка сервисов...")
        try:
            backend_process.terminate()
            frontend_process.terminate()
            
            # Ждем завершения
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
        except subprocess.TimeoutExpired:
            backend_process.kill()
            frontend_process.kill()
        except Exception as e:
            print(f"⚠️  Ошибка остановки: {e}")
        
        print("✅ Система остановлена")
    
    return True

if __name__ == "__main__":
    main()