import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, Integer, ForeignKey, MetaData, Select

# Не забываем подставлять свой пароль и имя пользователя
DSN = 'postgresql://postgres:1604@localhost:5432/VKinder'  # Определяем параметры подключения к базе данных
engine = sqlalchemy.create_engine(DSN)  # Создаем движок подключения
Session = sessionmaker(bind=engine)  # Создаем сессию в которую передаем движок подключения
session = Session()  # Создаем объект сессии
metadata = MetaData()  # Создаем объект метаданных

users = Table('users', metadata,  # Создаем таблицу пользователя
              Column('id', Integer, primary_key=True),  # Присваиваем автоматический идентификатор пользователя
              Column('vk_user', String(30), nullable=False),  # Создаем поле vk_user с типом данных String
              Column('gender', String(15), nullable=False),  # String(15) - где 15 ограничение по количеству символов
              Column('age', String(20), nullable=False),
              Column('city', String(83), nullable=False))

pair = Table('pair', metadata,  # Создаем таблицу результата поиска людей по параметрам пользователя
             Column('id', Integer, primary_key=True),
             Column('first_name', String(60), nullable=False),
             Column('last_name', String(60), nullable=False),
             Column('city', String(200), nullable=False),
             Column('profile_url', String(200), nullable=False),
             Column('photos', String(1500), nullable=False))

favorite = Table('favorite', metadata,  # Создаем таблицу для обектов pair добавленных в избранное, для каждого users
                 Column('id', Integer, primary_key=True),
                 Column('users_id', Integer, ForeignKey('users.id')),
                 Column('pair_id', Integer, ForeignKey('pair.id')))


def create_table_in_base():  # Функция создания таблиц в базе данных используя объект MetaData
    metadata.create_all(engine)


# create_table_in_base()  # Вызов функции создания таблиц в базе данных

def push_user_data_in_base(vk_user, gender, age, city):
    if gender == 'Мужской':  # Фильтр по гендеру
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


def push_pair_data_in_base(first_name, last_name, city, profile_url, photos):
    insert_values = pair.insert().values(  # Определяем колонки и их значения для записи в базу
        first_name=first_name,  # Поле в базе = передаваемый элемент в функцию
        last_name=last_name,
        city=city,
        profile_url=profile_url,
        photos=photos
    )
    session.execute(insert_values)  # добавляем записи в базу
    session.commit()  # фиксируем изменения в базе
    session.close()  # закрываем соединение с базой


def push_pair_in_favorite(vk_id, pair_id):  # Добавляем user и pair в избранное, устанавливаем связь
    data = get_user_data(vk_id)  # Получаем данные users
    users_id = data[0]  # записываем id пользователя VK в переменную
    insert_values = favorite.insert().values(
        users_id=users_id,
        pair_id=pair_id
    )
    session.execute(insert_values)
    session.commit()
    session.close()


def get_user_data(vk_id):  # select запрос в таблицу users
    select_query = Select(users.c.id, users.c.gender, users.c.age, users.c.city
                          ).where(
        users.c.vk_user == str(vk_id))  # Указываем параметры select запроса, что достать и условие поиска
    result = session.execute(select_query)
    rows = result.fetchone()  # Вся информация интересующая нас лежит здесь
    session.close()
    return rows


def get_pair_data():  # select запрос в таблицу pair
    selection_query = Select(pair.c.id, pair.c.first_name, pair.c.last_name, pair.c.profile_url, pair.c.photos)
    result = session.execute(selection_query)  # Объект результата select запроса записываем в переменную
    rows = result.fetchall()  # Достаем результаты select запроса и также записываем в переменную
    session.close()
    return rows


def get_favorite_data(vk_user):  # select запрос в таблицу favorite
    selection_query = Select(
        pair.c.first_name, pair.c.last_name, pair.c.profile_url, pair.c.photos
    ).join(favorite, pair.c.id == favorite.c.pair_id  # Объединяем таблицы по принадлежности объекта pair и favorite
           ).join(users, favorite.c.users_id == users.c.id  # Объединяем таблицы по принадлежсти fsvorite и users
                  ).where(users.c.vk_user == str(vk_user))  # Определяем параметры запроса
    result = session.execute(selection_query)
    rows = result.fetchall()
    session.close()
    return rows