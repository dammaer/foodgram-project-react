![Foodgram workflow](https://github.com/dammaer/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Дипломный проект Яндекс.Практикум - Foodgram
### Описание:
Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

**Рабочий проект доступен по адресу** https://dammaer.ml

### Используемые технологии:
- **Python 3.9.5**
- **Django REST Framework 3.12.4**
- **Docker**
- **PostgreSQL 12.4**
- **Nginx**
- **Gunicorn 20.1.0**
- **Git**
- **Djoser (аутентификация на основе токенов)**


### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:dammaer/foodgram-project-react.git
cd foodgram-project-react/
```
Подготовить файл с переменными окружения (описание переменных в .env.template)
```
cd infra/
cp .env.template .env
```
Запустите docker-compose командой: 
```
docker-compose up -d
```
У вас развернётся проект, запущенный с использованием gunicorn и базой данных postgres.
После успешного запуска контейнеров выполните миграции и создайте суперпользователя:
```
docker-compose exec backend python manage.py makemirations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```
По желанию загрузите в БД подготовленные данные об ингридиентах из **csv** файла:
```
docker-compose exec backend python manage.py load_csv ./data/ingredients.csv
```

### Github actions
#### Workflow состоит из четырёх шагов:
- Тестирование проекта.
- Сборка и публикация образа.
- Автоматический деплой (dammaer.ml)
- Отправка уведомления в персональный чат (Telegram).
