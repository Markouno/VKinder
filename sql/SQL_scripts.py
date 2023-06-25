import sqlalchemy, json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, Integer, ForeignKey, MetaData


DSN = 'postgresql://postgres:1604@localhost:5432/VKinder'  # определяем параметры подключения к базе данных
engine = sqlalchemy.create_engine(DSN)  # создаем движок подключения
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()


users = Table('users', metadata,  # Создаем таблицу пользователя
              Column('id', Integer, primary_key=True),
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
def create_table_in_base():   # создание таблиц в базе данных
    metadata.create_all(engine)

# create_table_in_base()   # Вызов функции создания таблиц в базе данных


def user_data_push_in_base():

    with open('sql/json_data/user_data.json', 'r', encoding='UTF=8') as file:   # Чтение данных из JSON-файла
        json_data = json.load(file)

    insert_values = users.insert().values(   # Запись данных в базу дынных VKinder
        gender=json_data['gender'],
        age=json_data['age'],
        city=json_data['city']
    )

    session.execute(insert_values)   # добавляем записи в базу

    session.commit()   # фиксируем изменения в базе

    session.close()   # закрываем соединение с базой

user_data_push_in_base()
def search_hits_push_in_base():
    '''
    Чтение данных из JSON-файла
    '''
    with open('sql/json_data/pair_data.json', 'r', encoding='UTF=8') as file:
        json_data = json.load(file)
        '''
        Запись данных в базу дынных VKinder
        '''
    for data in json_data:
        pair_object = pair.insert().values(
            name=data['name'],
            lastname=data['lastname'],
            link_page=data['link_page'],
            link_photos=data['link_photos']
        )
        session.execute(pair_object)  # добавляем записи в базу

    session.commit()  # фиксируем изменения в базе

    session.close()  # закрываем соединение с базой


# def adding_to_favorites():   # пока не понимаю до конца какие данные будем заливать, оставлю на завтра
#     for item in favorite_check:
#         people_who_liked = favorite.insert().values(
#             users_id=item['users_id'],
#             pair_id=item['pair_id']
#         )
#         session.execute(people_who_liked)
#
#     session.commit()


# if __name__ == '__main__':
    # user_data_push_in_base()
    # search_hits_push_in_base()
    # adding_to_favorites()
