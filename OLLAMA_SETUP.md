# Установка и настройка Ollama для гибридного подхода

## Что такое гибридный подход?

Система автоматически выбирает лучший доступный вариант для анализа резюме:

1. **Gemini API** (приоритет 1) - лучшее качество, когда есть квота
2. **Ollama** (приоритет 2) - бесплатно, приемлемое качество, когда нет квоты Gemini
3. **Fallback** (приоритет 3) - базовое качество, всегда работает

## Установка Ollama

### Windows

1. Скачайте установщик: https://ollama.com/download/windows
2. Запустите установщик
3. Ollama автоматически запустится как сервис

### Linux/macOS

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Docker

```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Установка модели

После установки Ollama, скачайте модель:

### Рекомендуемая модель: Mistral 7B

```bash
ollama pull mistral
```

### Альтернативные модели:

```bash
# Llama 2 7B (хорошая поддержка русского)
ollama pull llama2

# Neural Chat (для диалогов)
ollama pull neural-chat

# Code Llama (для технических задач)
ollama pull codellama
```

## Проверка установки

```bash
# Проверить, что Ollama работает
ollama list

# Протестировать модель
ollama run mistral "Привет, как дела?"
```

## Настройка в проекте

### 1. Переменные окружения

Добавьте в `.env` файл (опционально, если используете значения по умолчанию):

```env
# Ollama настройки (опционально)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

**По умолчанию:**
- URL: `http://localhost:11434`
- Модель: `mistral`

### 2. Если Ollama на другом сервере

Если Ollama запущен на другом сервере:

```env
OLLAMA_URL=http://your-server-ip:11434
OLLAMA_MODEL=mistral
```

## Как это работает

### Автоматическое переключение

1. **Система пытается использовать Gemini API:**
   - Если успешно → использует Gemini (лучшее качество)
   - Если ошибка (429, timeout) → переходит к Ollama

2. **Если Gemini недоступен, использует Ollama:**
   - Если Ollama доступен → использует Ollama (приемлемое качество)
   - Если Ollama недоступен → переходит к Fallback

3. **Если ничего не работает, использует Fallback:**
   - Простые правила (базовое качество)
   - Всегда работает

### Логирование

В логах вы увидите, какой провайдер используется:

```
INFO: Concepts extracted via Gemini API
INFO: Resume analyzed via Gemini API

или

WARNING: Gemini API unavailable, trying Ollama
INFO: Concepts extracted via Ollama
INFO: Resume analyzed via Ollama

или

WARNING: Ollama unavailable, using fallback
INFO: Using fallback concept extraction
INFO: Using fallback resume analysis
```

## Производительность

### На CPU (без GPU):
- Время анализа: 3-7 секунд на резюме
- Для 50 резюме: ~3-6 минут

### На GPU (NVIDIA):
- Время анализа: 0.5-1 секунда на резюме
- Для 50 резюме: ~30-60 секунд

## Требования к ресурсам

### Минимальные (CPU):
- RAM: 8-16 GB
- CPU: 4+ ядер
- Диск: 10 GB свободного места

### Рекомендуемые (GPU):
- GPU: NVIDIA с 6+ GB VRAM (RTX 3060+)
- RAM: 16 GB
- CPU: 4+ ядер

## Проверка работы

После установки Ollama, запустите тест:

```bash
cd backend
python scripts/test_parser_gemini.py
```

Система автоматически:
1. Попробует Gemini API
2. Если не работает → попробует Ollama
3. Если не работает → использует Fallback

## Отключение Ollama

Если хотите отключить Ollama (использовать только Gemini + Fallback):

1. Не устанавливайте Ollama
2. Или остановите сервис Ollama
3. Система автоматически пропустит Ollama и перейдет к Fallback

## Устранение проблем

### Ollama не запускается

```bash
# Проверить статус
ollama serve

# Перезапустить
ollama serve
```

### Модель не найдена

```bash
# Проверить установленные модели
ollama list

# Установить модель
ollama pull mistral
```

### Медленная работа

- Используйте GPU вместо CPU
- Или используйте более легкую модель (но качество будет хуже)

## Преимущества гибридного подхода

✅ **Максимальное качество** - когда Gemini доступен
✅ **Бесплатно** - когда Gemini недоступен, использует Ollama
✅ **Стабильность** - всегда есть Fallback
✅ **Приватность** - Ollama работает локально
✅ **Без ограничений** - Ollama не имеет лимитов

## Следующие шаги

1. Установите Ollama
2. Скачайте модель (mistral)
3. Запустите тест
4. Наслаждайтесь гибридным подходом! 🚀
