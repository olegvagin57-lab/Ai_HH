# Настройка GitHub Secrets для CI/CD

Этот файл содержит инструкции по настройке секретов в GitHub для автоматической сборки и деплоя.

## Важно: Безопасность

**НИКОГДА не коммитьте пароли и секретные ключи в код!** Все секреты должны храниться в GitHub Secrets.

## Настройка Docker Hub Secrets

### Шаг 1: Перейдите в настройки репозитория

1. Откройте ваш репозиторий: https://github.com/olegvagin57-lab/Ai_HH
2. Перейдите в **Settings** (Настройки)**
3. В левом меню выберите **Secrets and variables** → **Actions**

### Шаг 2: Добавьте секреты

Нажмите **New repository secret** и добавьте следующие секреты:

#### DOCKER_USERNAME
- **Name**: `DOCKER_USERNAME`
- **Secret**: `olegvagin57@gmail.com`
- **Важно**: Docker Hub позволяет использовать email как username

#### DOCKER_PASSWORD
- **Name**: `DOCKER_PASSWORD`
- **Secret**: `[ваш пароль Docker Hub]`
- **Важно**: Пароль должен быть актуальным для вашего аккаунта

### Шаг 3: Проверка

После добавления секретов, они будут доступны в GitHub Actions workflows через:
```yaml
${{ secrets.DOCKER_USERNAME }}
${{ secrets.DOCKER_PASSWORD }}
```

## Настройка Secrets для Production Deployment (опционально)

Если вы хотите настроить автоматический деплой на продакшн сервер, добавьте следующие секреты:

### PRODUCTION_HOST
- **Name**: `PRODUCTION_HOST`
- **Secret**: IP адрес или домен вашего продакшн сервера
- **Пример**: `192.168.1.100` или `yourdomain.com`

### PRODUCTION_USER
- **Name**: `PRODUCTION_USER`
- **Secret**: Имя пользователя для SSH подключения
- **Пример**: `deploy` или `ubuntu`

### PRODUCTION_SSH_KEY
- **Name**: `PRODUCTION_SSH_KEY`
- **Secret**: Приватный SSH ключ для подключения к серверу
- **Как получить**: 
  ```bash
  # На сервере
  ssh-keygen -t ed25519 -C "github-actions"
  # Скопируйте содержимое ~/.ssh/id_ed25519 (приватный ключ)
  ```

### STAGING_HOST (опционально)
- **Name**: `STAGING_HOST`
- **Secret**: IP адрес или домен staging сервера

### STAGING_USER (опционально)
- **Name**: `STAGING_USER`
- **Secret**: Имя пользователя для SSH на staging

### STAGING_SSH_KEY (опционально)
- **Name**: `STAGING_SSH_KEY`
- **Secret**: Приватный SSH ключ для staging

### SLACK_WEBHOOK_URL (опционально)
- **Name**: `SLACK_WEBHOOK_URL`
- **Secret**: URL вебхука Slack для уведомлений о деплое

## Проверка работы

После настройки секретов:

1. Сделайте push в ветку `main` или `master`
2. GitHub Actions автоматически запустит workflow
3. Проверьте статус в разделе **Actions** вашего репозитория
4. Workflow должен успешно залогиниться в Docker Hub и собрать образы

## Устранение проблем

### Ошибка: "Username and password required"
- Убедитесь, что секреты `DOCKER_USERNAME` и `DOCKER_PASSWORD` добавлены правильно
- Проверьте, что имена секретов точно совпадают (регистр важен)
- Убедитесь, что вы не добавили лишних пробелов

### Ошибка: "authentication required"
- Проверьте правильность пароля Docker Hub
- Убедитесь, что аккаунт Docker Hub активен
- Проверьте, что у аккаунта есть права на создание репозиториев

## Безопасность

- **Не делитесь** этими секретами публично
- **Не коммитьте** секреты в код
- **Регулярно обновляйте** пароли
- Используйте **2FA** для Docker Hub аккаунта
- Используйте **отдельные аккаунты** для CI/CD если возможно

## Ссылки

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Docker Hub Authentication](https://docs.docker.com/docker-hub/access-tokens/)
