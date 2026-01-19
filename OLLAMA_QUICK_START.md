# Быстрый старт Ollama для Windows

## Шаг 1: Установка Ollama

### Вариант A: Через winget (рекомендуется)

```powershell
winget install Ollama.Ollama
```

### Вариант B: Скачать установщик

1. Откройте https://ollama.com/download
2. Скачайте установщик для Windows
3. Запустите установщик и следуйте инструкциям

### Вариант C: Через скрипт

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_ollama.ps1
```

## Шаг 2: Запуск Ollama

После установки Ollama должна запуститься автоматически. Если нет:

```powershell
# Запуск Ollama сервера
ollama serve
```

Оставьте это окно открытым - Ollama должна работать в фоне.

## Шаг 3: Установка модели

Откройте **новый** терминал PowerShell и выполните:

```powershell
# Установка модели Mistral (рекомендуется, ~4GB)
ollama pull mistral

# Или более легкая модель Llama2 (~3.8GB)
ollama pull llama2

# Или самая быстрая модель (но хуже качество)
ollama pull tinyllama
```

**Рекомендация:** Используйте `mistral` - хороший баланс качества и скорости.

## Шаг 4: Проверка работы

```powershell
# Проверка, что Ollama работает
curl http://localhost:11434/api/tags

# Или через PowerShell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

Должен вернуться список установленных моделей.

## Шаг 5: Настройка проекта

### Проверьте `.env` файл:

```env
# Убедитесь, что эти строки есть (или добавьте)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### Если `.env` нет, создайте его:

```powershell
cd backend
# Создайте .env файл с настройками Ollama
@"
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
"@ | Out-File -FilePath .env -Encoding UTF8
```

## Шаг 6: Перезапуск backend

```powershell
# Остановите текущий backend (Ctrl+C)
# Затем запустите снова
cd backend
uvicorn app.main:app --reload --port 8000
```

В логах вы должны увидеть:
```
[INFO] Ollama is available, url=http://localhost:11434, model=mistral
```

## Шаг 7: Тестирование

```powershell
cd backend
python scripts/test_hybrid_ai.py
```

Вы должны увидеть:
```
Hugging Face: ✅ Доступен
Ollama: ✅ Доступен
```

## ✅ Готово!

Теперь Ollama будет автоматически использоваться для анализа резюме, если:
- Gemini недоступен
- Hugging Face недоступен
- Ollama доступна (запущена)

## 🔧 Устранение проблем

### Проблема: "ollama: command not found"

**Решение:**
1. Перезапустите PowerShell после установки
2. Или добавьте Ollama в PATH вручную

### Проблема: Ollama не запускается

**Решение:**
```powershell
# Проверьте, не запущена ли уже Ollama
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}

# Если не запущена, запустите вручную
ollama serve
```

### Проблема: Модель не найдена

**Решение:**
```powershell
# Проверьте установленные модели
ollama list

# Если модели нет, установите
ollama pull mistral
```

### Проблема: Backend не видит Ollama

**Решение:**
1. Убедитесь, что Ollama запущена: `ollama serve`
2. Проверьте URL в `.env`: `OLLAMA_BASE_URL=http://localhost:11434`
3. Перезапустите backend
4. Проверьте логи backend

## 📊 Рекомендуемые модели

| Модель | Размер | Скорость | Качество | Рекомендация |
|--------|--------|----------|----------|--------------|
| `mistral` | 4.1GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Лучший выбор |
| `llama2` | 3.8GB | ⭐⭐⭐ | ⭐⭐⭐ | Хороший вариант |
| `llama2:13b` | 7.3GB | ⭐⭐ | ⭐⭐⭐⭐⭐ | Для лучшего качества |
| `tinyllama` | 637MB | ⭐⭐⭐⭐⭐ | ⭐⭐ | Только для тестов |

## 💡 Полезные команды

```powershell
# Список установленных моделей
ollama list

# Удаление модели
ollama rm mistral

# Запуск интерактивного чата с моделью
ollama run mistral

# Проверка использования ресурсов
ollama ps
```
