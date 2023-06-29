import sqlalchemy, json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, Integer, ForeignKey, MetaData, Select
from tqdm import tqdm


DSN = 'postgresql://postgres:Markouno123@localhost:5432/VKinder'  # Определяем параметры подключения к базе данных
engine = sqlalchemy.create_engine(DSN)  # Создаем движок подключения
Session = sessionmaker(bind=engine)  # Создаем сессию в которую передаем движок подключения
session = Session()
metadata = MetaData()


users = Table('users', metadata,  # Создаем таблицу пользователя
              Column('id', Integer, primary_key=True),
              Column('vk_user', String(30), nullable=False),
              Column('gender', String(15), nullable=False),
              Column('age', String(20), nullable=False),
              Column('city', String(83), nullable=False)
              )

pair = Table('pair', metadata,  # Создаем таблицу результата поиска людей по параметрам пользователя
             Column('id', Integer, primary_key=True),
             Column('first_name', String(60), nullable=False),
             Column('last_name', String(60), nullable=False),
             Column('city', String(200), nullable=False),
             Column('profile_url', String(200), nullable=False),
             Column('photos', String(1500), nullable=False)
             )

favorite = Table('favorite', metadata,  # Создаем таблицу связей первых двух таблиц
                 Column('id', Integer, primary_key=True),
                 Column('users_id', Integer, ForeignKey('users.id')),
                 Column('pair_id', Integer, ForeignKey('pair.id')),
                 )

city = Table('city', metadata,  # Создаем таблицу с данными id всех населенных пунктов, их - 157710шт.
             Column('id', Integer, primary_key=True),
             Column('city_id', String(15), nullable=False),
             Column('title', String(100), nullable=False),
             Column('area', String(100)),
             Column('region', String(100)),
             )


def create_table_in_base():  # Функция создания таблиц в базе данных используя объекты MetaData
    metadata.create_all(engine)


# create_table_in_base()  # Вызов функции создания таблиц в базе данных


def user_data_push_in_base():
    with open('sql/json_data/user_data.json', 'r', encoding='UTF-8') as file:  # Чтение данных из JSON-файла
        json_data = json.load(file)
    insert_values = users.insert().values(  # Определяем колонки и их значения для записи в базу
        vk_user=json_data['vk_user'],
        gender=json_data['gender'],
        age=json_data['age'],
        city=json_data['city']
    )

    session.execute(insert_values)  # добавляем записи в базу

    session.commit()  # фиксируем изменения в базе

    session.close()  # закрываем соединение с базой


# user_data_push_in_base()   # Вызов функции записи данных пользователя



def search_hits_push_in_base():

    with open('sql/json_data/pair_data.json', 'r', encoding='UTF-8') as file:
        json_data = json.load(file)

    for data in json_data:
        pair_object = pair.insert().values(
            # Определяем колонки и их значения для записи в базу. Запись данных в базу дынных VKinder
            first_name=data['first_name'],
            last_name=data['last_name'],
            city= data['city'],
            profile_url=data['profile_url'],
            photos=data['photos']
        )
        session.execute(pair_object)  # добавляем записи в базу

    session.commit()  # фиксируем изменения в базе

    session.close()  # закрываем соединение с базой

# search_hits_push_in_base()


# search_hits_push_in_base()   #   Вызов функции записи данных в базу, результата парсинга по параметрам пользователя


def city_id_push_in_base():  # Запись данных city_id в базу данных
    with open('json_data/city_id_database.json', 'r', encoding='UTF-8') as file:
        json_data = json.load(file)

    for data in tqdm(json_data):  # Запускаем цикл со счетчиком tqdm
        city_object = city.insert().values(
            city_id=data.get('id'),
            title=data.get('title'),
            area=data.get('area'),   # Если ключа и значения нет, то get() вернет None
            region=data.get('region')   # Если ключа и значения нет, то get() вернет None
        )
        session.execute(city_object)  # добавляем записи в базу

    session.commit()  # фиксируем изменения в базе

    session.close()  # закрываем соединение с базой


# city_id_push_in_base()  # Вызов функции записи данных city_id в базу данных
# Объявляем цель select запроса в базу VKinder и таблицу users

def get_user_data():  # select запрос в таблицу users
    session = Session()  # Создаем новую сессию
    select_query = Select(users.c.gender, users.c.age, users.c.city).where(
        users.c.vk_user == vk_id)  # Указываем параметры select запроса, что достать и условие поиска
    result = session.execute(select_query)
    rows = result.fetchall()  # Вся информация интересующая нас лежит здесь
    session.close()  # Закрываем сессию
    return rows

# get_user_data()   # Вызываем функцию для проверки, но только в дебагере, чтобы увидеть результат
