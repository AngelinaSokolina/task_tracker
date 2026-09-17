# Task Tracker API

Backend-сервис для трекера задач сотрудников. Руководитель ставит задачи сотрудникам, отмечает их тип (срочная / повседневная / информационная), сотрудники видят свои задачи и меняют их статус.

## Стек технологий

- **Python 3.12** + **Django 6.0**
- **Django REST Framework** — API
- **PostgreSQL 15** — база данных
- **JWT** (`djangorestframework-simplejwt`) — авторизация по номеру телефона
- **django-filter** — фильтрация задач
- **drf-yasg** — OpenAPI-документация (Swagger / ReDoc)
- **Docker** + **Docker Compose** — контейнеризация
- **Nginx** — обратный прокси
- **GitHub Actions** — CI/CD

## Архитектура

[Браузер] → [Nginx:80] → [Django + Gunicorn:8000] → [PostgreSQL:5432]


## Роли

| Роль | Возможности |
|------|-------------|
| **Руководитель (manager)** | Видит все задачи, создаёт задачи, регистрирует сотрудников, смотрит статусы |
| **Сотрудник (employee)** | Видит только свои задачи, меняет их статус, оставляет комментарии |

## Типы задач

| Тип | Цвет на календаре |
|-----|-------------------|
| `urgent` — срочная | 🔴 красный |
| `daily` — повседневная | 🔵 синий |
| `info` — информационная | 🟢  зелёный |

## Статусы задач

- `in_progress` — в процессе
- `done` — выполнено

## Запуск через Docker (рекомендуемый способ)

### 1. Клонировать репозиторий

```
git clone https://github.com/AngelinaSokolina/task_tracker.git
cd task_tracker
```

### 2. Создать .env из шаблона
```
cp .env.docker .env
```

### 3. Запустить контейнеры
```
docker compose up -d --build
```

### 4. Создать суперпользователя
```
docker compose exec web python manage.py createsuperuser
```
Вас спросят:

Телефон (логин) — например, +79990000000

ФИО — например, Иванов Иван

Пароль — минимум 8 символов

### 5. Открыть в браузере
Swagger: http://localhost/docs/

ReDoc: http://localhost/redoc/

Админка: http://localhost/admin/

### Остановка
```
docker compose down
```
## Запуск без Docker (для разработки)
### 1. Создать и активировать виртуальное окружение

```
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
```
### 2. Установить зависимости

```
pip install -r requirements.txt
```

### 3. Поднять только базу данных в Docker

```
docker compose up -d db
```

### 4. Применить миграции и запустить сервер

```
python manage.py migrate
python manage.py runserver
```
Сервер будет доступен по адресу: http://127.0.0.1:8000

## API эндпоинты

### Авторизация

Метод | URL | Описание  
---|---|---  
POST | `/api/token/` | Получение JWT-токенов по телефону и паролю  
POST | `/api/token/refresh/` | Обновление access-токена  

### Пользователи
Метод | URL | Кто | Описание  
---|---|---|---  
POST | `/api/users/register/` | manager | Регистрация сотрудника (возвращает сгенерированный пароль)  
GET | `/api/users/me/` | любой | Текущий пользователь  
GET | `/api/users/` | любой | Список пользователей  
GET | `/api/users/{id}/` | любой | Один пользователь  
PUT | `/api/users/{id}/` | любой | Обновление пользователя  
PATCH | `/api/users/{id}/` | любой | Частичное обновление  
DELETE | `/api/users/{id}/` | любой | Удаление пользователя  

### Задачи
Метод | URL | Кто | Описание  
---|---|---|---  
GET | `/api/tasks/` | все | Список задач (manager — все, employee — только свои)  
POST | `/api/tasks/` | manager | Создание задачи  
GET | `/api/tasks/{id}/` | все | Одна задача  
PUT | `/api/tasks/{id}/` | manager | Полное обновление задачи  
PATCH | `/api/tasks/{id}/` | manager | Частичное обновление задачи  
DELETE | `/api/tasks/{id}/` | manager | Удаление задачи  
PATCH | `/api/tasks/{id}/status/` | любой | Смена статуса задачи  

### Комментарии
Метод | URL | Описание  
---|---|---  
GET | `/api/tasks/{task_id}/comments/` | Список комментариев задачи  
POST | `/api/tasks/{task_id}/comments/` | Добавить комментарий  

### Фильтры для /api/tasks/
Параметр | Значения | Описание  
---|---|---  
date | YYYY-MM-DD | Фильтр по дате  
type | urgent / daily / info | Фильтр по типу задачи  
status | in_progress / done | Фильтр по статусу  
assignee | {id} | Фильтр по исполнителю  

### Типы задач
Тип | Цвет на календаре | Описание  
---|---|---  
urgent | 🔴 красный | Срочная задача  
daily | 🔵 синий | Повседневная задача  
info | 🟢 зелёный | Информационная задача  

### Статусы задач
Статус | Описание  
---|---  
in_progress | В процессе  
done | Выполнено  

### Роли
Роль | Возможности  
---|---  
Руководитель (manager) | Видит все задачи, создаёт задачи, регистрирует сотрудников, смотрит статусы  
Сотрудник (employee) | Видит только свои задачи, меняет их статус, оставляет комментарии  

### Переменные окружения
Переменная | Описание | Пример  
---|---|---  
SECRET_KEY | Секретный ключ Django | django-insecure-...  
DEBUG | Режим отладки | False  
ALLOWED_HOSTS | Разрешённые хосты | localhost,127.0.0.1  
POSTGRES_DB / NAME | Имя базы данных | task_tracker_db  
POSTGRES_USER / USER | Пользователь БД | postgres  
POSTGRES_PASSWORD / PASSWORD | Пароль БД | postgres  
HOST | Хост БД | db (в Docker), localhost (локально)  
PORT | Порт БД | 5432 (в Docker), 5433 (локально)  
CORS_ALLOWED_ORIGINS | Разрешённые источники CORS | http://localhost  


## Примеры запросов
### Регистрация сотрудника (только manager)
```commandline
curl -X POST http://localhost/api/users/register/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+79991112233",
    "full_name": "Иванов Иван Иванович",
    "position": "Бухгалтер"
  }'
```
**Ответ:**

```{
  "id": 2,
  "phone": "+79991112233",
  "full_name": "Иванов Иван Иванович",
  "position": "Бухгалтер",
  "generated_password": "fIxzQr5eh9Y"
}
```

### Создание задачи (только manager)
```commandline
curl -X POST http://localhost/api/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Составить отчёт по финансам",
    "description": "До конца недели",
    "type": "urgent",
    "assignee": 2,
    "date": "2026-09-15",
    "status": "in_progress"
  }'
```

### Смена статуса задачи (сотрудник)
```curl -X PATCH http://localhost/api/tasks/1/status/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
  ```

## Тесты
Проект покрыт тестами (покрытие 97%).

### Запуск всех тестов
```
python manage.py test
```
### Запуск с покрытием

```
coverage run --source='.' manage.py test
coverage report
coverage html  # создаст отчёт htmlcov/index.html
```
### Запуск всех тестов
```
python manage.py test
```
## Запуск отдельных приложений
```
python manage.py test users
python manage.py test tasks
```
## Линтинг и форматирование
```
flake8 . --exclude=.venv,migrations,htmlcov --max-line-length=120 --extend-ignore=E203,W503
black .
isort .
```

## CI/CD (GitHub Actions)
Файл .github/workflows/ci.yml описывает пайплайн:

1. test — запускается на push и PR:
* Поднимает PostgreSQL
* Устанавливает зависимости
* Прогоняет flake8
* Прогоняет тесты с проверкой покрытия (порог 75%)

2. deploy — запускается только при push в main:
* Подключается по SSH к серверу Yandex Cloud
* Делает git pull и docker compose up -d --build


## Автор
_Ангелина Соколовская_



 
 