import vk_api, random, time, json, requests
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from tokens import community_token, user_token
from create_filter import create_filter
from sql.SQL_scripts import *
from main import VK_Parse
from tqdm import tqdm


vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)

answer_list = ['Привет!', 'Приветствую!', 'Здравствуйте!', 'Здарова!']
hello_list = ['Привет', 'привет', 'Салам', 'салам', 'Хай', 'хай', 'Здарова', 'здарова']

def write_msg(user_id, message, keyboard=None):
    parametrs = {'user_id': user_id,
                 'message': message,
                 'random_id': random.randrange(10 ** 7)
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
            
            
            if request == 'Начать':
                # chat_button = VkKeyboard()
                # chat_button.add_button('Тест', VkKeyboardColor.PRIMARY)
                # chat_button.add_button('Второй тест', VkKeyboardColor.SECONDARY)

                write_msg(event.user_id, f"{random.choice(answer_list)}")
                write_msg(event.user_id, f'Подскажи, кого мы ищем? Укажи через запятую пол, возраст и город.')
                write_msg(event.user_id, f'Пример: Мужской, 26, Москва')
            
            elif len(filter_list) == 3:
                gender = filter_list[0]
                age = filter_list[1]
                city = filter_list[2]
                write_msg(event.user_id, f'Начинаю поиск по параметрам: {gender}, {age}, {city}.')
                write_msg(event.user_id, f'Это займет какое-то время...')
                create_filter(filter_list, event.user_id)
                user_data_push_in_base()
                vk_parser = VK_Parse(user_token, age, age, 2)
                vk_parser.parse()
                write_msg(event.user_id, f'Сортируем плохих и хороших...')
                search_hits_push_in_base()
                write_msg(event.user_id, f'Готово! Начинаем?')


                
                
                


            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

        