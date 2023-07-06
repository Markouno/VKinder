import vk_api
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from tokens import community_token, user_token
from sql.SQL_scripts import *
from parser_vk import VK_Parse


vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)

answer_list = ['Привет!', 'Приветствую!', 'Здравствуйте!', 'Здарова!']
hello_list = ['Привет', 'привет', 'Салам',
              'салам', 'Хай', 'хай', 'Здарова', 'здарова']


def write_msg(user_id, message, keyboard=None, attachment=None):
    parametrs = {'user_id': user_id,
                 'message': message,
                 'random_id': random.randrange(10 ** 7),
                 "attachment": attachment
                 }

    if keyboard != None:
        parametrs['keyboard'] = keyboard.get_keyboard()
    else:
        parametrs = parametrs

    vk.method('messages.send', parametrs)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text
            filter_list = event.text.split(', ')
            chat_button = VkKeyboard(inline=True)  # Инициализация кнопок
            if request == 'Начать' or request in hello_list:
                write_msg(
                    event.user_id, f'{random.choice(answer_list)}')  # Приветствие от бота пользователю
                write_msg(
                    event.user_id, f'Подскажи, кого мы ищем?&#128527;\nУкажи через запятую пол, возраст и город.\nПример: Мужской, 26, Москва')

            # Данное условие ГРУБО даёт понять, что боту переданы параметры для поиска
            elif len(filter_list) == 3:
                gender = filter_list[0]
                age = filter_list[1]
                city = filter_list[2]
                write_msg(
                    event.user_id, f'Начинаю поиск по параметрам: {gender}, {age}, {city}.\nЭто займет менее минуты...')
                # Метод для записи параметров поиска в базу данных users
                push_user_data_in_base(event.user_id, gender, age, city)
                vk_parser = VK_Parse(user_token, gender, age, city)
                vk_parser.parse()  # Начало парсинга совпадений
                chat_button.add_button('Да', VkKeyboardColor.POSITIVE)
                chat_button.add_button('Нет', VkKeyboardColor.NEGATIVE)
                write_msg(
                    event.user_id, f'Готово! Начинаем?', chat_button)

            elif request == 'Да':
                chat_button.add_button('Нравится', VkKeyboardColor.POSITIVE)
                chat_button.add_button('Дальше', VkKeyboardColor.NEGATIVE)
                chat_button.add_button('Показать избранных', VkKeyboardColor.SECONDARY)
                pair_list = get_pair_data(event.user_id)  # Метод, возвращающий совпадения из базы данных
                for item in pair_list:
                    # Присваиваем переменные
                    id, first_name, last_name, page, photos = item[0], item[1], item[2], item[3], item[4]
                    # Убираем срезом фигурные скобки после селекта из базы
                    photos = photos[1: -1]
                    write_msg(
                        event.user_id, f'{first_name} {last_name}\n{page}', chat_button, photos)
                    for event in longpoll.listen():  # Новый лонг-пулл для получения реакции от пользователя
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            request = event.text
                            if request == 'Нравится':
                                push_pair_in_favorite(event.user_id, id) # Метод записи избранных в таблицу favorite
                                break

                            elif request == 'Дальше':
                                break

                            elif request == 'Показать избранных':
                                favorite_data = get_favorite_data(event.user_id)
                                for item in favorite_data:
                                    first_name, last_name, page, photos = item[0], item[1], item[2], item[3]
                                    photos = photos[1: -1]
                                    write_msg(
                                        event.user_id, f'{first_name} {last_name}\n{page}', None, photos)

            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")