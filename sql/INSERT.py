import json
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from CREATE import users, pair, favorite


DSN = 'postgresql://postgres:1604@localhost:5432/VKinder'
engine = db.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()



user_data = [{
    'gender': '1',
    'age': '26',
    'city': 'Майкоп'
}]

search_hits = [{
    'name': 'Анна',
    'lastname': 'Иванова',
    'link_page': 'https://vk.com/id1',
    'link_photos': [
        'https://sun6-22.userapi.com/impf/rD7Ugfhcf7bKIJ4-d8l8I-RkaTwVN-IRoxt9sg/heuH_mKDOcY.jpg?size=771x1080&quality=96&sign=081954f67c15e03ffdfe34f3673040f1&type=album',
        'https://sun6-23.userapi.com/impf/c830408/v830408095/e9b55/VSGEsuDKwUE.jpg?size=1280x640&quality=96&sign=073fa390aaa25fc7efc3d1ddb3605c10&type=album',
        'https://sun6-20.userapi.com/impf/c623900/v623900095/1160b2/39ZyjmEB_1Y.jpg?size=1279x959&quality=96&sign=fd54b29846172edd00944b5802e9b659&type=album'
    ]
}]

favorite_check = [{'user_id': 1,'pair_id': 1}]


def user_data_push_in_base():
    for item in user_data:
        user = users.insert().values(   #   user - это всего лишь объект
            gender=item['gender'],
            age=item['age'],
            city=item['city']
        )
        session.execute(user)   # добавляем записи

    session.commit()   # фиксируем изменения


def search_hits_push_in_base():
    for item in search_hits:
        pair_object = pair.insert().values(
            name=item['name'],
            lastname=item['lastname'],
            link_page=item['link_page'],
            link_photos=item['link_photos']
        )
        session.execute(pair_object)

    session.commit()


def adding_to_favorites():
    for item in favorite_check:
        people_who_liked = favorite.insert().values(
            users_id=item['user_id'],
            pair_id=item['pair_id']
        )
        session.execute(people_who_liked)

    session.commit()


if __name__ == '__main__':
    # user_data_push_in_base()
    # search_hits_push_in_base()
    adding_to_favorites()
