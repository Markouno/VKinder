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
              'салам', 'Хай', 'хай', 'Здарова', 'здарова',
              'Начать', 'Start', 'Начать поиск']


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
                    event.user_id, f'&#128269; Начинаю поиск по параметрам: {gender}, {age}, {city}.\nЭто займет менее минуты...')

                vk_parser = VK_Parse(
                    user_token, event.user_id, gender, age, city)
                parser_data = vk_parser.parse()  # Начало парсинга совпадений
                bad_answer = f'&#10060; Ошибка:\nОдин или несколько параметров указаны неверно.\nПопробуйте ещё раз.'
                if parser_data == bad_answer:
                    write_msg(event.user_id, bad_answer)
                else:
                    # Метод для записи параметров поиска в базу данных users
                    push_user_data_in_base(event.user_id, gender, age, city)
                    chat_button.add_button(
                        'Давай посмотрим', VkKeyboardColor.POSITIVE)
                    chat_button.add_button('Нет', VkKeyboardColor.NEGATIVE)
                    write_msg(
                        event.user_id, f'{parser_data} Начинаем?', chat_button)

            elif request == 'Давай посмотрим':
                chat_button.add_button('Нравится', VkKeyboardColor.POSITIVE)
                chat_button.add_button('Дальше', VkKeyboardColor.NEGATIVE)
                chat_button.add_button('Стоп', VkKeyboardColor.SECONDARY)
                # Метод, возвращающий совпадения из базы данных
                pair_list = get_pair_data(event.user_id)
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
                                # Метод записи избранных в таблицу favorite
                                push_pair_in_favorite(event.user_id, id)
                                break

                            elif request == 'Дальше':  # Переход к next итерации
                                break

                            elif request == 'Стоп':  # Остановка итератора и выход из цикла for
                                break
                        elif request == 'Стоп':
                            break
                    if request == 'Стоп':
                        menu_button = VkKeyboard(inline=True)
                        menu_button.add_button(
                            'Начать поиск', VkKeyboardColor.POSITIVE)
                        menu_button.add_button(
                            'Избранные', VkKeyboardColor.SECONDARY)
                        write_msg(event.user_id, f'Что делаем?', menu_button)
                        break
            elif request == 'Нет':
                write_msg(event.user_id, f'Что делаем?', menu_button)

            elif request == 'Избранные':  # Конструкция для импорта данных из базы
                favorite_data = get_favorite_data(event.user_id)
                for item in favorite_data:
                    first_name, last_name, page, photos = item[0], item[1], item[2], item[3]
                    photos = photos[1: -1]
                    write_msg(
                        event.user_id, f'{first_name} {last_name}\n{page}', None, photos)
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")