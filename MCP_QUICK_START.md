# 🚀 Быстрый старт: MCP серверы

## Что такое MCP?

MCP (Model Context Protocol) - это протокол, который позволяет AI-ассистенту получать доступ к различным ресурсам и инструментам для более эффективной работы с вашим проектом.

## 🎯 Полезные MCP серверы для проекта анализа резюме

### ✅ Уже готовы к использованию:

1. **Filesystem** - доступ к файлам проекта
2. **Sequential Thinking** - пошаговое мышление для сложных задач
3. **Playwright** - автоматизация браузера и E2E тестирование
4. **WCGW** - анализ рисков и выявление проблем
5. **Git** - работа с Git репозиторием
6. **MongoDB** - прямой доступ к базе данных
7. **Puppeteer** - автоматизация браузера
8. **SQLite** - локальная БД для тестирования

### ⚙️ Требуют настройки:

1. **Context 7** - нужен `CONTEXT7_API_KEY`
2. **GitHub** - нужен `GITHUB_PERSONAL_ACCESS_TOKEN`
3. **Brave Search** - нужен `BRAVE_API_KEY`

## 📋 Быстрая настройка

### Вариант 1: Через настройки Cursor

1. Откройте Cursor Settings (Ctrl+,)
2. Найдите "MCP Servers" или "Model Context Protocol"
3. Добавьте конфигурацию из файла `mcp.config.template.json`

### Вариант 2: Через файл конфигурации

1. Скопируйте `mcp.config.template.json` в:
   - Windows: `%APPDATA%\Cursor\User\globalStorage\mcp.json`
   - Mac: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
   - Linux: `~/.config/Cursor/User/globalStorage/mcp.json`

2. Заполните необходимые API ключи (если нужны)

3. Перезапустите Cursor

## 🔑 Получение API ключей

### Context 7 API Key:
1. Зарегистрируйтесь на Context7
2. Получите API ключ
3. Добавьте в `.env`: `CONTEXT7_API_KEY=your_key`

### GitHub Token:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Создайте токен с правами: `repo`, `workflow`
3. Добавьте в `.env`: `GITHUB_PERSONAL_ACCESS_TOKEN=your_token`

### Brave Search API Key:
1. Зарегистрируйтесь на https://brave.com/search/api/
2. Получите API ключ
3. Добавьте в `.env`: `BRAVE_API_KEY=your_key`

## ✅ Проверка работы

После настройки попросите AI-ассистента:
- "Прочитай файл README.md" (Filesystem)
- "Покажи последние коммиты" (Git)
- "Сколько резюме в базе?" (MongoDB)

## 📚 Подробная документация

См. [MCP_SERVERS_SETUP.md](MCP_SERVERS_SETUP.md) для детальной информации.
