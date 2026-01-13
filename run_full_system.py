#!/usr/bin/env python3
"""
Скрипт для запуска полной системы HH Resume Analyzer
Запускает backend и frontend одновременно
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run_command_in_background(command, cwd=None, name="Process"):
    """Запуск команды в фоновом режиме"""
    try:
        print(f"🚀 Запуск {name}...")
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        return process
    except Exception as e:
        print(f"❌ Ошибка запуска {name}: {e}")
        return None

def check_dependencies():
    """Проверка зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    # Проверка Python зависимостей
    backend_requirements = Path("backend/requirements.txt")
    if backend_requirements.exists():
        print("✅ Backend requirements найдены")
    else:
        print("❌ Backend requirements не найдены")
        return False
    
    # Проверка Node.js зависимостей
    frontend_package = Path("frontend/package.json")
    if frontend_package.exists():
        print("✅ Frontend package.json найден")
    else:
        print("❌ Frontend package.json не найден")
        return False
    
    return True

def install_dependencies():
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    
    # Установка Python зависимостей
    print("📦 Установка Python зависимостей...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Ошибка установки Python зависимостей: {result.stderr}")
        return False
    
    # Установка Node.js зависимостей
    print("📦 Установка Node.js зависимостей...")
    result = subprocess.run([
        "npm", "install"
    ], cwd="frontend", capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Ошибка установки Node.js зависимостей: {result.stderr}")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def main():
    """Главная функция"""
    print("🎯 HH Resume Analyzer - Запуск полной системы")
    print("=" * 50)
    
    # Проверка зависимостей
    if not check_dependencies():
        print("❌ Не все зависимости найдены")
        install_deps = input("Установить зависимости? (y/n): ")
        if install_deps.lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            sys.exit(1)
    
    processes = []
    
    try:
        # Запуск Backend
        backend_process = run_command_in_background(
            f"{sys.executable} -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload",
            cwd="backend",
            name="Backend API"
        )
        if backend_process:
            processes.append(("Backend", backend_process))
        
        # Ждем запуска backend
        print("⏳ Ожидание запуска backend...")
        time.sleep(5)
        
        # Запуск Frontend
        frontend_process = run_command_in_background(
            "npm start",
            cwd="frontend",
            name="Frontend React App"
        )
        if frontend_process:
            processes.append(("Frontend", frontend_process))
        
        print("\n" + "=" * 50)
        print("🎉 Система запущена!")
        print("📍 Backend API: http://localhost:8000")
        print("📍 Frontend App: http://localhost:3000")
        print("📍 API Docs: http://localhost:8000/docs")
        print("=" * 50)
        print("💡 Нажмите Ctrl+C для остановки всех сервисов")
        
        # Ожидание завершения
        while True:
            time.sleep(1)
            # Проверяем, что процессы еще работают
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} завершился")
    
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        # Остановка всех процессов
        print("🛑 Остановка сервисов...")
        for name, process in processes:
            if process.poll() is None:
                print(f"🛑 Остановка {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"⚠️  Ошибка остановки {name}: {e}")
        
        print("✅ Все сервисы остановлены")

if __name__ == "__main__":
    main()