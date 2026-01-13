# 🚀 Ручной запуск системы

## Проблема
Автоматические команды не выполняются через Kiro. Нужно запускать вручную.

## ✅ Что работает
- ✅ Frontend установлен и готов (npm install завершен)
- ✅ Backend код написан
- ✅ Все файлы созданы

## 🎯 Ручной запуск

### 1. Простой тест backend
Откройте **новый терминал** и выполните:
```bash
cd C:\Users\User\.kiro\Projects\HH_AI
python test_simple_backend.py
```

Должно появиться:
```
🚀 Starting simple backend...
📍 API: http://localhost:8000
📍 Docs: http://localhost:8000/docs
💡 Press Ctrl+C to stop
```

### 2. Проверка в браузере
Откройте браузер и перейдите по адресам:
- http://localhost:8000 - должен показать "HH Resume Analyzer Backend is running!"
- http://localhost:8000/docs - документация API

### 3. Запуск frontend
Откройте **еще один терминал** и выполните:
```bash
cd C:\Users\User\.kiro\Projects\HH_AI\frontend
npm start
```

Frontend запустится на http://localhost:3000 или http://localhost:3001

## 🔧 Если простой backend работает

Тогда можно попробовать полный backend:

### 1. Остановите простой backend (Ctrl+C)

### 2. Запустите полный backend:
```bash
cd C:\Users\User\.kiro\Projects\HH_AI\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📍 Ожидаемые адреса

После успешного запуска:
- **Frontend**: http://localhost:3000 или http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎯 Тестирование системы

1. **Откройте frontend** в браузере
2. **Нажмите "Войти"** в правом верхнем углу
3. **Выберите "Зарегистрироваться"**
4. **Заполните форму** и создайте аккаунт
5. **Попробуйте создать поиск** резюме

## ❌ Если что-то не работает

### Frontend не запускается:
```bash
cd frontend
npm install
npm start
```

### Backend ошибки:
1. Проверьте, что Python установлен: `python --version`
2. Установите зависимости: `pip install -r backend/requirements.txt`
3. Проверьте файл `backend/.env`

### Ошибки авторизации:
- Убедитесь, что backend запущен на порту 8000
- Проверьте консоль браузера (F12)
- Очистите localStorage браузера

## 🎉 Результат

Если все работает, вы увидите:
- ✅ Рабочий frontend с формами авторизации
- ✅ Backend API с документацией
- ✅ Возможность регистрации и входа
- ✅ Интерфейс для создания поисков резюме

**Система готова к использованию!** 🚀