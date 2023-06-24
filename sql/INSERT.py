import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from CREATE import users, pair, favorite


DSN = 'postgresql://postgres:1604@localhost:5432/VKinder'
engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()

favorite_check = [{'users_id': 1,'pair_id': 1}]


def user_data_push_in_base():
    '''
    Чтение данных из JSON-файла
    '''
    with open('json_data/user_data.json', 'r', encoding='UTF=8') as file:
        json_data = json.load(file)
        '''
        Запись данных в базу дынных VKinder
        '''
    insert_values = users.insert().values(
        gender=json_data['gender'],
        age=json_data['age'],
        city=json_data['city']
    )

    session.execute(insert_values)   # добавляем записи в базу

    session.commit()   # фиксируем изменения в базе

    session.close()   # закрываем соединение с базой


def search_hits_push_in_base():
    '''
    Чтение данных из JSON-файла
    '''
    with open('json_data/pair_data.json', 'r', encoding='UTF=8') as file:
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


def adding_to_favorites():   # пока не понимаю до конца какие данные будем заливать, оставлю на завтра
    for item in favorite_check:
        people_who_liked = favorite.insert().values(
            users_id=item['users_id'],
            pair_id=item['pair_id']
        )
        session.execute(people_who_liked)

    session.commit()


if __name__ == '__main__':
    user_data_push_in_base()
    search_hits_push_in_base()
    # adding_to_favorites()
