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

Метод `parse` — основной метод, отвечающий за поиск пользователей. Он использует **VK API**, делая запрос `users.search` с заданными параметрами.
Используя параметры в инициализаторе метод возвращает совпадения, после чего применяет
метод `get_photos` для парсинга фотографий пользователей и записывает мета-дату по одному в базу данных
при помощи функции `pair_data_push_in_base`, импортированной из собственного модуля **SQL_scripts**.

```
def parse(self):
    params = {'count': '1000',
            'sex': self.gender,
            'hometown': self.city,
            'age_from': self.age,
            'age_to': self.age,
            'has_photo': '1',
            'access_token': self.access_token,
            'v': '5.131'
            }
    response = requests.get(
            'https://api.vk.com/method/users.search', params=params)
    result = response.json()
    try:
        if result['response']['count'] != 0:
            res = result['response']['items']
            for item in tqdm(res, desc='Идет поиск...'):
                
                profile_url = f"https://vk.com/id{item['id']}"
                photos = self.get_photos(item['id'])
                if photos:
                    first_name = item['first_name']
                    last_name = item['last_name']
                    city = self.city
                    push_pair_data_in_base(self.vk_user_id, first_name, last_name, city, profile_url, photos)
            return 'Всё готово!'
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

**Таблица пользователей, которые передали запросы на поиск знакомств.**
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

Функция `create_table_in_base()` создаёт эти отношения в базе данных.

## 💿 Insert запросы

### 💾 Push user data in base

Полученные параметры поиска от пользователя записываем в базу и параллельно передаем парсеру, **id** записываем для дальнейшего поиска записанных пар для конкретного пользователя.
В функцию передаем **id_VK** пользователя, начавшего общение с ботом, пол, возраст, и город, где **id** нам требуется для создания отношений и дальнейшего поиска отношений по конкретному пользователю, используя функции модуля `session: execute`(выполнить), `commit`(фиксация изменений в базе) и `close`(закрываем соединения с базой).

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
        vk_id=vk_id,
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

Передаем в функцуию **vk_id(id Вконтакте)**, так как нам нужны для извлечения только результаты поиска определенного участника беседы, для дальнейшей передачи их собеседнику бота по одному (цикл над полученными данными применяется за пределами данного скрипта)

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

Функция используется для выдачи пользователю уже отсортированных им личностей. Функция принимает в качестве агрумента **vk_id**, далее путем объединения отношений используя связь многие ко многим, мы отслеживаем все записи в базе данных, имеющих связь с **id** из аргумента функции - `get_favorite_data()` и извлекаем их с помощью функции `execute()(модуля session)`, и указываем что нам нужны все совпадения используя функцию `fetchall()`.

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

**Echo bot vk** - центр управления и мозг этого организма. Данный модуль использует библиотеку VK-API для взаимодействия с пользователем.
Режим для прослушивания событий инициализируется путем цикла `for event in longpoll.listen():`. В этом режиме бот "слушает" события от пользователя, а конкретно новые сообщения `VkEventType.MESSAGE_NEW`.

```
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text
```

Блок, отвечающий за приветствие и возможность парсинга начинается здесь:

```
if request == 'Начать' or request in hello_list:
    write_msg(
        event.user_id, f'{random.choice(answer_list)}')
    write_msg(
        event.user_id, f'Подскажи, кого мы ищем?&#128527;\nУкажи через запятую пол, возраст и город.\nПример: Мужской, 26, Москва')
```

Благодаря блоку `filter_list = event.text.split(', ')` бот умеет разделять сообщения на переменные, которые будут использоваться в парсинге:

```
elif len(filter_list) == 3:
    gender = filter_list[0]
    age = filter_list[1]
    city = filter_list[2]
```

Далее параметры передаются в переменную `vk_parser`, которая является экземпляром класса `VK_Parse` и после чего вызывается функция `vk_parser.parse()` из импортированного модуля.

```
vk_parser = VK_Parse(user_token, event.user_id, gender, age, city)
parser_data = vk_parser.parse()
```

После проверки парсера на ошибки будет запущен блок кода с ожиданием ответа от пользователя, в котором происходит запись параметров поиска в базу данных и инициализация кнопок для ответа на сообщение:

```
else:
    push_user_data_in_base(event.user_id, gender, age, city)            
    chat_button.add_button('Давай посмотрим', VkKeyboardColor.POSITIVE)
    chat_button.add_button('Нет', VkKeyboardColor.NEGATIVE)
    write_msg(
        event.user_id, f'{parser_data} Начинаем?', chat_button)
```

В случае, если пользователь выбирает посмотреть список найденых людей:
* Происходит инициализация кнопок
* Вызывается метод `get_pair_data`, возвращающий совпадения из базы данных
* Запускается итерация для выдачи совпадения по одному

```
elif request == 'Давай посмотрим':
    chat_button.add_button('Нравится', VkKeyboardColor.POSITIVE)
    chat_button.add_button('Дальше', VkKeyboardColor.NEGATIVE)
    chat_button.add_button('Стоп', VkKeyboardColor.SECONDARY)
    pair_list = get_pair_data(event.user_id)
    for item in pair_list:
        id, first_name, last_name, page, photos = item[0], item[1], item[2], item[3], item[4]
        photos = photos[1: -1]
        write_msg(
            event.user_id, f'{first_name} {last_name}\n{page}', chat_button, photos)
```

Далее бот снова переходит в режим "прослушивания" благодаря конструкции `for event in longpoll.listen()`:
* Нравится - вызывается функция записи в базу
* Дальше - переход на следующую итерацию без записи
* Стоп - полная остановка данного блока и выход в условное "меню" первичных условий бота

```
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text
        if request == 'Нравится':
            push_pair_in_favorite(event.user_id, id)
            break

        elif request == 'Дальше':
            break

        elif request == 'Стоп':
                break
```

Меню для выбора действий:
* Начать поиск - обновление всего кода
* Избранные - метод для отображения избранных

```
if request == 'Стоп':
    menu_button = VkKeyboard(inline=True)
    menu_button.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
    menu_button.add_button('Избранные', VkKeyboardColor.SECONDARY)
    write_msg(event.user_id, f'Что делаем?', menu_button)
    break
```

Избранные - блок кода, возвращающий всех понравившихся людей:

```
elif request == 'Избранные':
    favorite_data = get_favorite_data(event.user_id)
    for item in favorite_data:
        first_name, last_name, page, photos = item[0], item[1], item[2], item[3]
        photos = photos[1: -1]
        write_msg(
            event.user_id, f'{first_name} {last_name}\n{page}', None, photos)
```

___
We are coderz.

Expect us.