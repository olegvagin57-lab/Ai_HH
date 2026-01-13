# 🚀 START HERE - HH Resume Analyzer

## ✅ Services Are Starting!

Все сервисы запускаются. Подождите 10-15 секунд, затем:

### 1. Откройте в браузере:
**http://localhost:3000**

### 2. Зарегистрируйте нового пользователя:
- Email: ваш@email.com
- Username: ваш_username
- Password: минимум 8 символов, заглавная, строчная буква, цифра

### 3. Войдите в систему

### 4. Создайте первый поиск:
- **Query:** например, "Python developer with FastAPI"
- **City:** например, "Москва"
- Нажмите "Start Search"

### 5. Дождитесь результатов и изучите их!

## 📊 Полезные ссылки:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🔍 Проверка статуса:

Запустите в PowerShell:
```powershell
.\check_services.ps1
```

## ⚠️ Если что-то не работает:

1. **Backend не отвечает?**
   - Подождите еще 10-15 секунд
   - Проверьте: http://localhost:8000/health
   - Убедитесь, что MongoDB запущен

2. **Frontend не загружается?**
   - Проверьте консоль браузера (F12)
   - Убедитесь, что порт 3000 свободен

3. **Поиск не обрабатывается?**
   - Проверьте, что Celery worker запущен
   - Redis опционален, но рекомендуется

## 🎉 Готово к использованию!

Приятной работы с HH Resume Analyzer!
