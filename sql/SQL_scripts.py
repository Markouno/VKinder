import sqlalchemy, json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, Integer, ForeignKey, MetaData, Select
from tqdm import tqdm
from pprint import pprint

# Не забываем подставлять свои пароль и имя пользователя
DSN = 'postgresql://postgres:Markouno123@localhost:5432/VKinder'  # Определяем параметры подключения к базе данных
engine = sqlalchemy.create_engine(DSN)  # Создаем движок подключения
Session = sessionmaker(bind=engine)  # Создаем сессию в которую передаем движок подключения
session = Session()  # Создаем объект сессии
metadata = MetaData()

users = Table('users', metadata,  # Создаем таблицу пользователя
              Column('id', Integer, primary_key=True),
              Column('vk_user', String(30), nullable=False),
              Column('gender', String(15), nullable=False),
              Column('age', String(20), nullable=False),
              Column('city', String(83), nullable=False))

pair = Table('pair', metadata,  # Создаем таблицу результата поиска людей по параметрам пользователя
             Column('id', Integer, primary_key=True),
             Column('first_name', String(60), nullable=False),
             Column('last_name', String(60), nullable=False),
             Column('city', String(200), nullable=False),
             Column('profile_url', String(200), nullable=False),
             Column('photos', String(1500), nullable=False))

favorite = Table('favorite', metadata,  # Создаем таблицу связей первых двух таблиц
                 Column('id', Integer, primary_key=True),
                 Column('users_id', Integer, ForeignKey('users.id')),
                 Column('pair_id', Integer, ForeignKey('pair.id')))

def create_table_in_base():  # Функция создания таблиц в базе данных используя объекты MetaData
    metadata.create_all(engine)

# create_table_in_base()  # Вызов функции создания таблиц в базе данных

def user_data_push_in_base(vk_user, gender, age, city):
    if gender == 'Мужской':
        gender = '2'
    else:
        gender = '1'
    insert_values = users.insert().values(  # Определяем колонки и их значения для записи в базу
        vk_user=vk_user,
        gender=gender,
        age=age,
        city=city
    )
    session.execute(insert_values)  # добавляем записи в базу
    session.commit()  # фиксируем изменения в базе
    session.close()  # закрываем соединение с базой

# user_data_push_in_base()   # Вызов функции записи данных пользователя

def pair_data_push_in_base(first_name, last_name, city, profile_url, photos):
    pair_object = pair.insert().values( # Определяем колонки и их значения для записи в базу. Запись данных в базу дынных VKinder
        first_name=first_name,
        last_name=last_name,
        city=city,
        profile_url=profile_url,
        photos=photos
        )
    session.execute(pair_object)  # добавляем записи в базу
    session.commit()  # фиксируем изменения в базе
    session.close()  # закрываем соединение с базой

# search_hits_push_in_base()   #   Вызов функции записи данных в базу, результата парсинга по параметрам пользователя

def push_pair_in_favorite(vk_id, pair_id):   # Добавляем user и pair в избранное, устанавливаем связь
    new_data = get_user_data(vk_id)   # Получаем данные users
    users_id = new_data[0]   # берем id user
    insert_values = favorite.insert().values(
        users_id=users_id,
        pair_id=pair_id
    )
    session.execute(insert_values)
    session.commit()
    session.close()

# push_pair_in_favorite()   # Вызов функции записи избранных пар

def get_user_data(vk_id):  # select запрос в таблицу users
    session = Session()  # Создаем новую сессию
    select_query = Select( users.c.id, users.c.gender, users.c.age, users.c.city
    ).where(users.c.vk_user == str(vk_id))  # Указываем параметры select запроса, что достать и условие поиска
    result = session.execute(select_query)
    rows = result.fetchone()  # Вся информация интересующая нас лежит здесь
    session.close()  # Закрываем сессию
    return rows

def get_pair_data():  # select запрос в таблицу pair
    selection_query = Select(pair.c.id, pair.c.first_name, pair.c.last_name, pair.c.profile_url, pair.c.photos)
    result = session.execute(selection_query)
    rows = result.fetchall()
    session.close()
    return rows

# pprint(get_pair_data())   # Проверка функции

def get_favorite_data(vk_user):   # select запрос в таблицу favorite
    selection_query = Select(
        pair.c.first_name, pair.c.last_name, pair.c.profile_url, pair.c.photos
        ).join(favorite, pair.c.id == favorite.c.pair_id
        ).join(users, favorite.c.users_id == users.c.id
        ).where(users.c.vk_user == str(vk_user))
    result = session.execute(selection_query)
    rows = result.fetchall()
    session.close()
    return rows