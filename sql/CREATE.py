import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, String, Integer, ForeignKey, MetaData   # Импортируем элементы библиотеки для удобочитаемости кода


DSN = 'postgresql://postgres:1604@localhost:5432/VKinder'   # определяем параметры подключения к базе данных
engine = sqlalchemy.create_engine(DSN)   # создаем движок подключения
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()


users = Table('users', metadata,   # Создаем таблицу пользователя
    Column('id', Integer, primary_key=True),
    Column('gender', String(15), nullable=False),
    Column('age', String(20), nullable=False),
    Column('city', String(83), nullable=False)
)


pair = Table('pair', metadata,   # Создаем таблицу результата поиска людей по параметрам пользователя
    Column('id', Integer, primary_key=True),
    Column('name', String(60), nullable=False),
    Column('lastname', String(60), nullable=False),
    Column('link_page', String(200), nullable=False),
    Column('link_photos', String(500), nullable=False)
)


favorite = Table('favorite', metadata,   # Создаем таблицу связей первых двух таблиц
    Column('id', Integer, primary_key=True),
    Column('users_id', Integer, ForeignKey('users.id')),
    Column('pair_id', Integer, ForeignKey('pair.id')),
)

def create_table():   # Создаем таблицы в нашей базе данных
    metadata.create_all(engine)


if __name__ == '__main__':  # Определяем точку входа
    create_table()