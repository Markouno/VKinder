import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from tokens import community_token
from create_filter import create_filter
import random



vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)

answer_list = ['Привет!', 'Приветствую!', 'Здравствуйте!', 'Здарова!']
hello_list = ['Привет', 'привет', 'Салам', 'салам', 'Хай', 'хай', 'Здарова', 'здарова']

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': random.randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text
            filter_list = event.text.split(', ')

            if request == 'Начать':
                write_msg(event.user_id, f"{random.choice(answer_list)}")
                write_msg(event.user_id, f'Подскажи, кого мы ищем? Укажи через запятую пол, возраст и город.')
                write_msg(event.user_id, f'Пример: Мужской, 26, Москва')
            
            elif len(filter_list) == 3:
                write_msg(event.user_id, f'Начинаю поиск по параметрам: {filter_list[0]}, {filter_list[1]}, {filter_list[2]}.')
                write_msg(event.user_id, f'Это займет какое-то время...')
                create_filter(filter_list)

            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

        