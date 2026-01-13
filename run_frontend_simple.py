#!/usr/bin/env python3
"""
Простой скрипт для запуска frontend без PowerShell
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Запуск frontend"""
    print("🚀 Запуск Frontend...")
    
    # Переходим в папку frontend
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Папка frontend не найдена")
        return False
    
    # Проверяем package.json
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json не найден")
        return False
    
    # Проверяем node_modules
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Установка зависимостей...")
        try:
            # Используем cmd вместо PowerShell
            result = subprocess.run([
                "cmd", "/c", "npm install"
            ], cwd=frontend_dir, check=True, capture_output=True, text=True)
            print("✅ Зависимости установлены")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки зависимостей: {e.stderr}")
            return False
    
    # Запускаем frontend
    print("🚀 Запуск React приложения...")
    try:
        # Используем cmd для запуска
        subprocess.run([
            "cmd", "/c", "npm start"
        ], cwd=frontend_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска frontend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Frontend остановлен")
    
    return True

if __name__ == "__main__":
    main()