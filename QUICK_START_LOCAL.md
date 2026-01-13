# Быстрый запуск без Docker

## Шаг 1: Запуск MongoDB (если не установлен локально)

Если MongoDB не установлен, можно использовать Docker только для MongoDB:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7
```

Или установите MongoDB локально: https://www.mongodb.com/try/download/community

## Шаг 2: Запуск Backend

```bash
cd backend
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend будет доступен на: http://localhost:8000

## Шаг 3: Создание тестового пользователя

В новом терминале:
```bash
py create_test_user_simple.py
```

## Шаг 4: Запуск Frontend

В новом терминале:
```bash
cd frontend
npm install  # если еще не установлено
npm start
```

Frontend будет доступен на: http://localhost:3000

## Данные для входа

**Администратор:**
- Email: `admin@test.com`
- Пароль: `admin123`

**HR Специалист:**
- Email: `hr@test.com`
- Пароль: `hr123`

## Проверка работы

1. Откройте http://localhost:3000
2. Войдите с данными администратора
3. Проверьте работу системы
