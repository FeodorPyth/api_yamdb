# api_yamdb
api_yamdb
## Описание проекта:
API для сервиса YaMDb, позволяющий собирает отзывы пользователей на произведения.

Для разработки использовался Django Rest Framework.

## Документация API:
Документация проекта представлена в формате Redoc и после запуска проекта будет доступна по адресу `http://127.0.0.1:8000/redoc/`.

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```sh
git clone git@github.com:FeodorPyth/api_final_yatube.git
```

```sh
cd kittygram
```

Cоздать и активировать виртуальное окружение:

```sh
python3 -m venv env
```

```sh
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```sh
python3 -m pip install --upgrade pip
```

```sh
pip install -r requirements.txt
```

Выполнить миграции:

```sh
python3 manage.py migrate
```

Запустить проект:

```sh
python3 manage.py runserver
```
