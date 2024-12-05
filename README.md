# BSW FastAPI

Этот проект состоит из двух связанных сервисов: Bet Maker и Line Provider, которые управляют событиями и ставками.

## 1. Line Provider

### Эндпоинты:

- GET /api_v1/events/: Получение списка всех активных событий.
- GET /api_v1/events/get_event: Получение события по event_id.
- GET /api_v1/events/get_past_events: Получение завершенных событий с результатами. Для событий, у которых прошел дедлайн, результат определяется рандомно и обновляется в БД. 
- POST /api_v1/events/create_event: Создание события.
- PUT /api_v1/events/update_event: Обновление события.
- DELETE /api_v1/events/delete_event/{event_id}: Удаление события.

## 2. Bet Maker

### Эндпоинты:

- GET /api_v1/events: Получение списка событий, доступных для ставок.
- GET /api_v1/bets: Получение истории всех сделанных ставок с указанием их текущего статуса (выиграла, проиграла, еще не сыграла).
- POST /api_v1/bet: Создание ставки на событие. В запросе передаются идентификатор события и сумма ставки.

## Технологии
Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, Docker

## Запуск проекта
- Скачайте проект: git clone https://github.com/EscapeFromHell/bsw-test-task.git
- После скачивания проекта, перейдите в папку проекта: cd bsw-test-task
- Выполните команду: docker compose up -d
- После запуска контейнеров, интерактивная документация будет доступна по ссылкам:

http://127.0.0.1:5000/docs - Line Provider

http://127.0.0.1:8000/docs - Bet Maker
