# Настройка Hugging Face API токена

## Что выбрать при создании токена

### 1. Token type (Тип токена)

**Выберите:** `Read` (самый простой вариант)

Или `Fine-grained` если хотите более детальный контроль (но для Inference API достаточно Read).

### 2. Token name (Имя токена)

Введите любое имя, например:
- `hh-resume-analyzer`
- `ai-analysis-token`
- `inference-api-token`

### 3. User permissions (Разрешения пользователя)

**Для Inference API нужно выбрать ТОЛЬКО:**

✅ **Inference:**
- ✅ **"Make calls to Inference Providers"** ← **ОБЯЗАТЕЛЬНО!**
- ⚠️ "Make calls to your Inference Endpoints" - опционально (если будете использовать свои endpoints)
- ❌ "Manage your Inference Endpoints" - не нужно

**Остальные разрешения НЕ нужны:**
- ❌ Repositories - не нужно
- ❌ Webhooks - не нужно
- ❌ Discussions & Posts - не нужно
- ❌ Collections - не нужно
- ❌ Billing - не нужно
- ❌ Jobs - не нужно

### 4. Repositories permissions

**Оставить пустым** - не нужно ничего выбирать.

### 5. Org permissions

**Оставить пустым** - не нужно ничего выбирать.

## Итоговый чеклист

✅ Token type: `Read` (или `Fine-grained`)
✅ Token name: любое имя (например, `hh-resume-analyzer`)
✅ User permissions → Inference → **"Make calls to Inference Providers"** ← ВАЖНО!
❌ Все остальное - не выбирать

## После создания токена

1. Скопируйте токен (он показывается только один раз!)
2. Добавьте в `.env` файл:
   ```env
   HUGGING_FACE_API_TOKEN=ваш_токен_здесь
   ```
3. Готово! Система автоматически начнет использовать Hugging Face.

## Важно

- Токен показывается только один раз при создании
- Сохраните его в безопасном месте
- Не публикуйте токен в Git
- Токен дает доступ к 30,000 бесплатным запросам/месяц
