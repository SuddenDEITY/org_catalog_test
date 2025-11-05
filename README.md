# Организационный каталог API

REST сервис каталога организаций, зданий и видов деятельности. Приложение построено на стекe FastAPI + SQLAlchemy + Alembic, использует `uv` в качестве менеджера зависимостей и работает с PostgreSQL.

## Возможности

- Фильтрация организаций по зданию, виду деятельности и названию.
- Рекурсивный поиск по дереву деятельностей (до 3 уровней вложенности).
- Геопоиск организаций в радиусе или прямоугольной области относительно точки.
- Просмотр перечня зданий и структуры видов деятельности.
- Аутентификация через статический API ключ (`X-API-Key`).
- Автоматические миграции и первичное заполнение БД тестовыми данными.

## Стек

- Python 3.12+
- FastAPI, Pydantic v2
- SQLAlchemy 2.x, Alembic
- PostgreSQL (по умолчанию), возможно переключение через `ORG_CATALOG_DATABASE_URL`
- uv (пакетный менеджер)

## Быстрый старт (uv)

1. Поднимите PostgreSQL (например, `docker compose up db`).
2. Установите зависимости и выполните миграции:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn org_catalog.main:app --host 0.0.0.0 --port 8000
```

> Для доступа к API укажите заголовок `X-API-Key: local-dev-key` или задайте собственный ключ через `ORG_CATALOG_API_KEY`.

## Запуск в Docker

```bash
docker compose up --build
```

Контейнер `db` разворачивает PostgreSQL 16, а `api` после прохода healthcheck применяет миграции и запускает Uvicorn на порту `8000`.

## Корневые переменные окружения

| Переменная | Назначение | Значение по умолчанию |
| --- | --- | --- |
| `ORG_CATALOG_API_KEY` | Статический API ключ | `local-dev-key` |
| `ORG_CATALOG_DATABASE_URL` | URL базы данных SQLAlchemy | `postgresql+asyncpg://postgres:postgres@localhost:5432/org_catalog` |
| `ORG_CATALOG_DEBUG` | Флаг режима debug | `false` |

## Основные эндпоинты

| Метод | Путь | Описание |
| --- | --- | --- |
| `GET` | `/api/v1/buildings` | Список зданий |
| `GET` | `/api/v1/buildings/{id}` | Данные здания |
| `GET` | `/api/v1/organizations/{id}` | Информация об организации |
| `GET` | `/api/v1/organizations/by-building/{building_id}` | Организации в здании |
| `GET` | `/api/v1/organizations/by-activity/{activity_id}` | Организации по виду деятельности (с учётом потомков) |
| `GET` | `/api/v1/organizations/search/by-activity?name=Еда` | Поиск организаций по названию деятельности (рекурсивно) |
| `GET` | `/api/v1/organizations/search/by-name?q=рога` | Поиск по названию организации |
| `GET` | `/api/v1/organizations/geo?latitude=55&longitude=37&radius_km=5` | Поиск в радиусе |
| `GET` | `/api/v1/organizations/geo?...&min_latitude=&max_latitude=&min_longitude=&max_longitude=` | Поиск в прямоугольнике |
| `GET` | `/api/v1/activities/tree` | Полное дерево деятельностей (макс. глубина 3) |
| `GET` | `/api/v1/activities/{id}/tree` | Поддерево по конкретной деятельности |

Интерактивная документация доступна по `/docs` (Swagger UI) и `/redoc`.

### Пример запроса

```bash
curl -H "X-API-Key: local-dev-key" \
     "http://localhost:8000/api/v1/organizations/search/by-name?q=рога"
```

## Структура данных

- **buildings** – адрес и координаты здания.
- **activities** – дерево видов деятельности (макс. 3 уровня вложенности).
- **organizations** – карточка организации, ссылки на здание и виды деятельности.
- **organization_phones** – связанные телефонные номера.

Миграции (`alembic/versions`) создают структуры и заполняют БД тестовыми данными.

## Разработка

- Конфигурация задаётся через переменные `ORG_CATALOG_*` или файл `.env` (пример поставляется вместе с проектом).
- Для пересборки схемы используйте `uv run alembic revision --autogenerate -m "message"`.
- Геопоиск реализован с помощью формулы гаверсинуса.
- Лимит глубины дерева деятельностей проверяется сервисным слоем.

## Тестирование

Перед запуском тестов установите dev-зависимости и убедитесь, что доступен Docker (Testcontainers автоматически поднимет PostgreSQL 16). Если задать `ORG_CATALOG_TEST_DATABASE_URL`, то будет использована указанная база.

```bash
uv run --extra dev pytest
```

Pytest применяет миграции, создаёт временную БД и очищает её по завершении сессии.
