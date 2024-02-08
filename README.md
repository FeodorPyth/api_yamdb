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
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```sh
python3 -m venv venv
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
## Особенности Проекта:
- [x] Настроена Аутентификация по токенам
- [x] Настроены разрешения в зависимости от типа запроса и авторизации клиента
- [x] Создана собственная модель User в соответствии с ТЗ
- [x] Разработана management-команда для заполнения БД с помощь csv-файлов
- [x] Создана система работы с рейтингами произведений
- [x] Настроена система комментариев и отзывов
- [x] Пройдены автотесты
- [x] Успешно пройдено код-ревью

## СТЕК технологий:
* Django
* Django Rest Framework
* Simplejwt
* Sqlite
* Pytest

## Наполнение БД с помощью транспортных файлов:
Единственный поддерживаемый формат файлов на данный момент - csv
Для наполнения БД необходимо разместить файлы в директорию: api_yamdb/static/data/

Обязательные требования к названиям и заголовкам файлов:
### Файл Категории
Название: category.csv
Структура заголовков: id,name,slug

### Файл Комментарии
Название: comments.csv
Структура заголовков: id,review_id,text,author_id,pub_date

### Файл Жанры
Название: genre.csv
Структура заголовков: id,name,slug

### Файл Вспомогательная таблица-связи Жанра и Произведения
Название: genre_title.csv
Структура заголовков: id,title_id,genre_id

### Файл Отзывы
Название: review.csv
Структура заголовков: id,title_id,text,author_id,score,pub_date

### Файл Произведения
Название: titles.csv
Структура заголовков: id,name,year,category_id

### Файл Пользователи
Название: users.csv
Структура заголовков: id,username,email,role,bio,first_name,last_name

Для запуска обработки файлов выполните следующие действия:
1. Перейдите в директорию с файлом manage.py:

```
cd /api_yamdb/api_yamdb
```

2. Выполните команду:
```
python manage.py load_csv_com
```

3. Для получения справки по команде load_csv_com выполните:
```
python manage.py load_csv_com -h
```

## Команда разработки:
1. [FeodorPyth](https://github.com/FeodorPyth) - Тимлид, Управление пользователями
2. [Hramovnik1043](https://github.com/Hramovnik1043) - Работа над ресурсами: Произведение, Жанры, Категории и создание csv-загрузчика
3. [mentxs](https://github.com/f1v3nt5) - Работа над ресурсами: Комментарии, Отзывы и Рейтинг
