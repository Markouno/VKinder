# 🧩 Модули

## 🕹️ parser_vk

Класс `class VK_Parse` инициализируется токеном доступа, полом, возрастом и городом. Access token используется для аутентификации запросов API.

На вход метод принимает токен, пол, возраст и город. Все в формате `str()`.
```
def __init__(self, access_token, gender, age, city):
        self.access_token = access_token
        self.age = age
        if gender == 'Мужской':
            gender = '2'
        else:
            gender = '1'
        self.gender = gender
        self.city = city
```
### 🖥️ Parse

Метод `parse` — основной метод, отвечающий за поиск пользователей. Он использует VK API, делая запрос `users.search` с заданными параметрами.

```
Здесь нужен парсер
```
### 📸 Get_photos

Метод `get_photos` анализирует фотографии для данного пользователя. Он делает запрос `photos.get` с указанными параметрами. Ответ обрабатывается, и из него извлекаются URL-адреса трех самых популярных (по лайкам) фотографий.

```
def get_photos(self, user_id):
        photos_params = {'owner_id': user_id,
                         'album_id': 'profile',
                         'rev': '1',
                         'access_token': self.access_token,
                         'extended': '1',
                         'v': '5.131'}
        try:
            photos_response = requests.get(
                'https://api.vk.com/method/photos.get', params=photos_params)
            photos_result = photos_response.json()
            photo_urls = []
            if 'response' in photos_result:
                photos = photos_result['response']['items']
                sorted_photos = sorted(photos, key=lambda x: x.get('likes', {}).get(
                    'count', 0), reverse=True)  # Сортировка по лайкам
                for photo in sorted_photos[:3]:
                    photo_urls.append(photo['sizes'][-1]['url'])
            return photo_urls
        except Exception as e:
            print(f"Ошибка при получении фотографий: {e}")
            return []
```



Извлеченные данные, включая URL-адрес профиля пользователя и URL-адреса фотографий, сохраняются в базе данных.
___

## 📚 SQL_scripts

Движок подключения использует библиотеку **SQLAlchemy** и **DSN** (параметры подключения).
Создается сессия подключения используя модуль `sessionmaker`, в который передается движок – **engine**.
Для использования подключения, необходим объект подключения, в который передается вызов сессии, которым запускается подключение к базе.

## ⛏️ Create запросы

Создание объектов записи отношений в базу данных.

Передача их в базу используя модуль `MetaData` из библиотеки **SQLAlchemy**.

**Таблица пользователей, который передали запросы на поиск знакомств.**
```
users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('vk_id', String(20), nullable=False),
              Column('gender', String(15), nullable=False),
              Column('age', String(20), nullable=False),
              Column('city', String(83), nullable=False))
```
**Таблица совпадений по указанным параметрам поиска**
```
pair = Table('pair', metadata,
             Column('id', Integer, primary_key=True),
             Column('vk_id', String(20), nullable=False),
             Column('first_name', String(60), nullable=False),
             Column('last_name', String(60), nullable=False),
             Column('city', String(200), nullable=False),
             Column('profile_url', String(200), nullable=False),
             Column('photos', String(1500), nullable=False))
```
**Таблица избранных**
```
favorite = Table('favorite', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('users_id', Integer, ForeignKey('users.id')),
                 Column('pair_id', Integer, ForeignKey('pair.id')))
```
Функция `create_table_in_base()` создаёт эти таблицы в базе данных.

## 💿 Insert запросы

### 💾 Push user data in base

Полученные параметры поиска от пользователя записываем в базу и параллельно передаем парсеру, **id** записываем для дальнейшего поиска записанных пар для конкретного пользователя.
В функцию передаем **id_VK** пользователя, начавшего общение с ботом, пол, возраст, и город, где **id** нам требуется для создания отношений и дальнейшего поиска отношений по конкретному пользователю, используя функции модуля `session: execute`(запись), `commit`(фиксация изменений в базе) и `close`(закрываем соединения с базой).

```
def push_user_data_in_base(vk_id, gender, age, city):
    if gender == 'Мужской':
        gender = '2'
    else:
        gender = '1'
    insert_values = users.insert().values(
        vk_user=vk_id,
        gender=gender,
        age=age,
        city=city
    )
    session.execute(insert_values)
    session.commit()
    session.close()
```

### 💾 Push pair data in base

Результаты запроса по указанным параметрам в функции выше, записываем в базу данных в таблицу **pair**, аналогично предыдущей функции вызываем функции модуля `session`, где **vk_id** – является **id**  VK собеседника бота.

```
def push_pair_data_in_base(vk_id, first_name, last_name, city, profile_url, photos):
    insert_values = pair.insert().values(  # Определяем колонки и их значения для записи в базу
        vk_user_id=vk_id,
        first_name=first_name,
        last_name=last_name,
        city=city,
        profile_url=profile_url,
        photos=photos
    )
    session.execute(insert_values)
    session.commit()
    session.close()
```

### 💾 Push pair data in favorite

Функция принимает **vk_id(PrimaryKey.table.users)** и **pair_id(PrimaryKey.table.pair)** и записываем их в таблицу **favorite**, где мы и устанавливаем связь конкретного пользователя и тех личностей, которых он добавил в избранное, то есть наполняем наш список избранных.

```
def push_pair_in_favorite(vk_id, pair_id):
    data = get_user_data(vk_id)
    users_id = data[0]
    insert_values = favorite.insert().values(
        users_id=users_id,
        pair_id=pair_id
    )
    session.execute(insert_values)
    session.commit()
    session.close()
```

## 🔌 Select запросы

### 🚩 Get user data

Передаем в функцуию **vk_id(id Вконтакте)**. Указываем какие поля нас интересуют, а именно **id(PrimaryKey.table.users)**, пол, возраст и город с условием, что значение в базе есть пользователь с указанным аргументом функуии - **vk_id**.

```
def get_user_data(vk_id):
    select_query = Select(users.c.id, users.c.gender, users.c.age, users.c.city
                          ).where(
        users.c.vk_id == str(vk_id))
    result = session.execute(select_query)
    rows = result.fetchone()
    session.close()
    return rows
```

### 🚩Get pair data

Функция не принимает аргументов, так как используется для извлечения всех элементов из таблицы **pair**, для дальнейшей передачи их собеседнику бота по одному (цикл над полученными данными применяется за пределами данного скрипта)

```
def get_pair_data(vk_id):
    selection_query = Select(pair.c.id, pair.c.first_name, pair.c.last_name, pair.c.profile_url, pair.c.photos
                             ).where(
        pair.c.vk_id == str(vk_id))
    result = session.execute(selection_query)
    rows = result.fetchall()
    session.close()
    return rows
```

### 🚩Get favorite data

Функция используется для выдачи пользователю уже отсортированных им личностей. Функция принимает в качестве агрумента **vk_user**, далее путем объединения таблиц используя связь многие ко многим, мы отслеживаем все записи в базе данных, имеющих связь с **id** из аргумента функции - `get_favorite_data()` и извлекаем их с помощью функции `execute()`, и указываем что нам нужны все совпадения используя функцию `fetchall()`.

```
def get_favorite_data(vk_id):
    selection_query = Select(
        pair.c.first_name, pair.c.last_name, pair.c.profile_url, pair.c.photos
    ).join(favorite, pair.c.id == favorite.c.pair_id
           ).join(users, favorite.c.users_id == users.c.id
                  ).where(users.c.vk_id == str(vk_id))
    result = session.execute(selection_query)
    rows = result.fetchall()
    session.close()
    return rows
```
___

## 🤖 Echo_bot_vk

```
Тут должна быть дока по боту
```




