# Быстрый старт: Hugging Face Integration

## Шаг 1: Создание токена

1. Откройте: https://huggingface.co/settings/tokens
2. Нажмите "New token"
3. Выберите:
   - **Token type:** `Read` (или `Fine-grained`)
   - **Token name:** `hh-resume-analyzer` (любое имя)
   - **User permissions → Inference:** ✅ **"Make calls to Inference Providers"**
   - Остальное не выбирать
4. Нажмите "Create token"
5. **Скопируйте токен** (показывается только один раз!)

## Шаг 2: Добавление токена в проект

Добавьте в `.env` файл (в корне проекта):

```env
HUGGING_FACE_API_TOKEN=ваш_токен_здесь
```

Или в `backend/.env`:

```env
HUGGING_FACE_API_TOKEN=ваш_токен_здесь
```

## Шаг 3: Тестирование

Запустите тест:

```bash
cd backend
python scripts/test_hybrid_ai.py
```

Или полный тест с парсером:

```bash
python scripts/test_parser_gemini.py
```

## Готово! 🎉

Теперь система будет использовать:
1. **Gemini API** (когда есть квота) - лучшее качество
2. **Hugging Face** (когда нет квоты Gemini) - отличное качество, 30K запросов/месяц бесплатно
3. **Ollama** (если установлен) - приемлемое качество
4. **Fallback** (всегда работает) - базовое качество

## Проверка работы

В логах вы увидите:
```
INFO: Concepts extracted via Hugging Face
INFO: Resume analyzed via Hugging Face
```

## Что дальше?

После добавления токена система автоматически начнет использовать Hugging Face когда Gemini недоступен!
