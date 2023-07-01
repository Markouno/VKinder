import vk_api, random, time, json, requests
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from tokens import community_token, user_token
from create_filter import create_filter
from sql.SQL_scripts import *
from parser_vk import VK_Parse
from tqdm import tqdm


vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)

answer_list = ['Привет!', 'Приветствую!', 'Здравствуйте!', 'Здарова!']
hello_list = ['Привет', 'привет', 'Салам', 'салам', 'Хай', 'хай', 'Здарова', 'здарова']

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
            chat_button = VkKeyboard(inline=True)
            if request == 'Начать':
                write_msg(event.user_id, f"{random.choice(answer_list)}")
                write_msg(event.user_id, f'Подскажи, кого мы ищем?&#128527;\n Укажи через запятую пол, возраст и город.\nПример: Мужской, 26, Москва')
            
            elif len(filter_list) == 3:
                gender = filter_list[0]
                age = filter_list[1]
                city = filter_list[2]
                write_msg(event.user_id, f'Начинаю поиск по параметрам: {gender}, {age}, {city}.\nЭто займет менее минуты...')
                create_filter(filter_list, event.user_id)
                user_data_push_in_base()
                vk_parser = VK_Parse(user_token, gender, age, city)
                vk_parser.parse()
                search_hits_push_in_base()
                chat_button.add_button('Да', VkKeyboardColor.POSITIVE)
                chat_button.add_button('Нет', VkKeyboardColor.NEGATIVE)
                write_msg(event.user_id, f'Готово! Начинаем?', chat_button)

            elif request == 'Да':
                chat_button.add_button('Нравится', VkKeyboardColor.POSITIVE)
                chat_button.add_button('Дальше', VkKeyboardColor.NEGATIVE)
                pair_list = get_pair_data()
                for item in pair_list:
                    first_name, last_name, page, photos = item[0], item[1], item[2], item[3]
                    photos = photos[1 : -1]
                    print(photos)
                    write_msg(event.user_id, f'{first_name} {last_name}\n{page}', chat_button, photos)
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            request = event.text
                            if request == 'Дальше' or '2':
                                break
                            elif request == 'Нравится' or '1':
                                # здесь должен быть инсерт в фавориты
                                break
                
                
                


            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

        