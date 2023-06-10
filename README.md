# praktikum_new_diplom

login = admin@mail.ru
password = admin
host = http://84.201.165.255/


# Проект Foodgram
## Автор:


[Sarugot](https://github.com/Sarugot)


## Описание:
### Проект Foodgram

Проект Foodgram позволяет пользователям создавать собственные рецепты и просматривать рецепты дрегих пользоваталей, добавлять рецепты в избранное, подписываться на авторов, скачивать список покупок.


## Технологии

Python 3.7

Django 3.2

Docker 3.8


## Шаблон наполнения env-файла:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```


## Описание команд для запуска приложения в контейнерах:

Перейти в папку с файлом docker-compose:

```
cd infra
```

Запустить контейнеры:

```
docker-compose up -d --build
```

Выполнить миграции:

```
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

Создать суперпользователя:

```
docker compose exec backend python manage.py createsuperuser
```

Собрать статику:

```
docker compose exec backend python manage.py collectstatic --no-input
```

Загрузить базу данных ингредиентов:

```
docker compose exec backend python manage.py ingredients_data
```


### Примеры запросов:

# Получение рецептов

Получить список всех рецептов. При указании параметров limit и offset выдача разделена по страницам.

```
GET /api/recipes/

{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

Responses

```
200 Удачное выполнение запроса.
```

# Создание рецептов

Добавление нового рецепта в коллекцию рецептов.

```
POST /api/recipes/

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Responses

```
201 Удачное выполнение запроса.

{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

```
400 Ошибка валидации.

{
  "field_name": [
    "Обязательное поле."
  ]
}
```

```
401 Запрос от имени анонимного пользователя.
```

```
404 Объект не найден.

{
  "detail": "Страница не найдена."
}
```
