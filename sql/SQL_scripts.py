import sqlalchemy, json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, Integer, ForeignKey, MetaData, Select


DSN = 'postgresql://postgres:1604@localhost:5432/VKinder'  # Определяем параметры подключения к базе данных
engine = sqlalchemy.create_engine(DSN)  # Создаем движок подключения
Session = sessionmaker(bind=engine)   # Создаем сессию в которую передаем движок подключения
session = Session()
metadata = MetaData()

'''
CREATE запросы
'''
users = Table('users', metadata,  # Создаем таблицу пользователя
              Column('id', Integer, primary_key=True),
              Column('vk_user', String(30), nullable=False),
              Column('gender', String(15), nullable=False),
              Column('age', String(20), nullable=False),
              Column('city', String(83), nullable=False)
              )

pair = Table('pair', metadata,  # Создаем таблицу результата поиска людей по параметрам пользователя
             Column('id', Integer, primary_key=True),
             Column('name', String(60), nullable=False),
             Column('lastname', String(60), nullable=False),
             Column('link_page', String(200), nullable=False),
             Column('link_photos', String(500), nullable=False)
             )

favorite = Table('favorite', metadata,  # Создаем таблицу связей первых двух таблиц
                 Column('id', Integer, primary_key=True),
                 Column('users_id', Integer, ForeignKey('users.id')),
                 Column('pair_id', Integer, ForeignKey('pair.id')),
                 )
def create_table_in_base():   # Функция создания таблиц в базе данных используя объекты MetaData
    metadata.create_all(engine)

# create_table_in_base()   # Вызов функции создания таблиц в базе данных

'''
INSERT запросы
'''
def user_data_push_in_base():

    with open('sql/json_data/user_data.json', 'r', encoding='UTF=8') as file:   # Чтение данных из JSON-файла
        json_data = json.load(file)

    insert_values = users.insert().values(   # Определяем колонки и их значения для записи в базу
        vk_user=json_data['vk_user'],
        gender=json_data['gender'],
        age=json_data['age'],
        city=json_data['city']
    )

    session.execute(insert_values)   # добавляем записи в базу

    session.commit()   # фиксируем изменения в базе

    session.close()   # закрываем соединение с базой

# user_data_push_in_base()   # Вызов функции записи данных пользователя
def search_hits_push_in_base():
    '''
    Чтение данных из JSON-файла
    '''
    with open('sql/json_data/pair_data.json', 'r', encoding='UTF=8') as file:   # Чтение данных из JSON-файла
        json_data = json.load(file)
        '''
        Запись данных в базу дынных VKinder
        '''
    for data in json_data:
        pair_object = pair.insert().values(   # Определяем колонки и их значения для записи в базу
            name=data['name'],
            lastname=data['lastname'],
            link_page=data['link_page'],
            link_photos=data['link_photos']
        )
        session.execute(pair_object)  # добавляем записи в базу

    session.commit()  # фиксируем изменения в базе

    session.close()  # закрываем соединение с базой

# search_hits_push_in_base()   #   Вызов функции записи данных в базу, результата парсинга по параметрам пользователя


'''
SELECT запросы
'''
vk_id = '790733692'   # Объявляем цель SELECT запроса в базу VKinder и таблицу users

def get_user_data():   # SELECT запрос в таблицу users
    session = Session()  # Создаем новую сессию
    select_query = Select(users.c.gender, users.c.age, users.c.city).where(users.c.vk_user == vk_id)  # Указываем параметры SELECT запроса, что достать и условие поиска
    result = session.execute(select_query)
    rows = result.fetchall()   # Вся информация интересующая нас лежит здесь
    session.close()  # Закрываем сессию
    return rows

get_user_data()   # Вызываем функцию для проверки, но только в дебагере, чтобы увидеть результат