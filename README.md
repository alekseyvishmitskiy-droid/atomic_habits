# Atomic Habits Tracker API

Бэкенд-часть SPA веб-приложения для трекинга полезных привычек, разработанная по мотивам книги Джеймса Клира «Атомные привычки».

## Стек технологий
* **Python / Django / Django REST Framework** — основа REST API
* **SimpleJWT** — аутентификация по JWT-токенам
* **PostgreSQL** — основная база данных
* **Celery + Redis** — отложенные и периодические задачи для отправки напоминаний
* **Telegram Bot API** — рассылка уведомлений пользователям
* **drf-spectacular** — автоматическая документация Swagger / ReDoc
* **Docker / Docker Compose / Nginx / Gunicorn** — контейнеризация и развертывание
* **GitHub Actions** — автоматизация тестирования, линтинга и деплоя (CI/CD)

## Функционал
* Регистрация и авторизация пользователей по email.
* CRUD-операции для личных привычек с пагинацией (по 5 привычек на страницу).
* Просмотр списка публичных привычек других пользователей (`GET /api/habits/public/`).
* Валидация бизнес-правил (время выполнения до 120 секунд, периодичность не реже 1 раза в 7 дней, разделение полезных и приятных привычек, запрет одновременного указания вознаграждения и связанной привычки).
* Ежеминутная проверка расписания через Celery Beat и отправка напоминаний в Telegram.

---

## Запуск проекта в Docker (рекомендуемый способ)

Все сервисы проекта (`web` на Gunicorn, `db` PostgreSQL, `redis`, `celery`, `celery-beat`, `nginx`) упакованы в контейнеры и запускаются одной командой.

1. **Клонируйте репозиторий:**
   ```bash
   git clone <ссылка_на_ваш_репозиторий>
   cd atomic_habits
   ```

2. **Создайте файл переменных окружения:**
   Скопируйте шаблон `.env.template` в `.env` и заполните значениями (укажите `SECRET_KEY`, параметры БД, `TELEGRAM_BOT_TOKEN` и `ALLOWED_HOSTS`):
   ```bash
   cp .env.template .env
   ```

3. **Соберите и запустите все сервисы одной командой:**
   ```bash
   docker compose up -d --build
   ```
   При старте автоматически применятся миграции базы данных и соберутся статические файлы. Приложение будет доступно через Nginx по адресу: `http://localhost/`.

4. **Остановка контейнеров:**
   ```bash
   docker compose down
   ```

---

## Локальный запуск без Docker

1. **Создайте виртуальное окружение и активируйте его:**
   ```bash
   python -m venv .venv
   # Для Windows:
   .venv\Scripts\activate
   # Для Linux/macOS:
   source .venv/bin/activate
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   Скопируйте `.env.template` в `.env` и заполните своими значениями.

4. **Примените миграции и запустите сервисы (в отдельных терминалах):**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   * Celery Worker (для Windows с флагом `-P eventlet`):
     ```bash
     celery -A config worker -l info -P eventlet
     ```
   * Celery Beat (планировщик):
     ```bash
     celery -A config beat -l info
     ```

---

## Настройка CI/CD и автоматического деплоя

В репозитории настроен пайплайн GitHub Actions (`.github/workflows/ci-cd.yml`), который запускается при `push` и `pull_request` в ветку `develop` и выполняет три этапа:
1. **Lint and Test:** проверка стиля кода с помощью `flake8` и запуск тестов Django с подключенными сервисами PostgreSQL и Redis.
2. **Build Docker:** авторизация в Docker Hub и тестовая сборка всех Docker-образов.
3. **Deploy:** при успешном слиянии изменений в ветку `develop` подключение к удаленному серверу по SSH, обновление кода (`git pull`) и перезапуск контейнеров (`docker compose up -d --build`).

### Подготовка удаленного сервера
1. Установите на сервер (Ubuntu) пакеты `docker.io`, `docker-compose-v2` и `git`.
2. Сгенерируйте SSH-ключ для деплоя и добавьте публичную часть в `~/.ssh/authorized_keys`.
3. Клонируйте репозиторий в директорию `~/atomic_habits`, переключитесь на ветку `develop` и создайте рабочий файл `.env` на основе `.env.template`.

### Настройка секретов в GitHub
В настройках репозитория (**Settings -> Secrets and variables -> Actions**) необходимо добавить следующие **Repository secrets**:
* `SERVER_HOST` — IP-адрес удаленного сервера.
* `SERVER_USER` — имя пользователя на сервере для подключения по SSH.
* `SSH_KEY` — приватный SSH-ключ для доступа к серверу.
* `DOCKER_USERNAME` — логин учетной записи Docker Hub.
* `DOCKERHUB_TOKEN` — токен доступа (Access Token) Docker Hub.

---

## Документация API
После запуска сервера интерактивная документация доступна по адресам:
* **Swagger UI:** `http://localhost/swagger/` (или `http://127.0.0` при запуске без Docker)
* **ReDoc:** `http://localhost/redoc/` (или `http://127.0.0` при запуске без Docker)

## Тестирование
Для запуска тестов и проверки покрытия выполните:
```bash
coverage run manage.py test
coverage report -m
```
Текущее покрытие кода тестами составляет **97%**.
