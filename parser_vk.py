from sql.SQL_scripts import *
import json
import requests
from tqdm import tqdm


class VK_Parse:
    # Инициализация входных параметров
    def __init__(self, access_token, vk_user_id, gender, age, city):
        self.access_token = access_token
        self.vk_user_id = vk_user_id
        self.age = age
        if gender == 'Мужской':
            gender = '2'
        else:
            gender = '1'
        self.gender = gender
        self.city = city

    def parse(self):
        '''
        Метод использует API-VK для парсинга пользователей
        Используя параметры в инициализаторе метод возвращает совпадения, после чего применяет
        метод get_photos для парсинга фотографий пользователей и записывает мета-дату по одному в базу данных
        при помощи функции pair_data_push_in_base, импортированной из собственного модуля SQL_scripts
        '''
        params = {'count': '1000',
                  'sex': self.gender,
                  'hometown': self.city,
                  'age_from': self.age,
                  'age_to': self.age,
                  'has_photo': '1',
                  'access_token': self.access_token,
                  'v': '5.131'
                  }
        response = requests.get(
            'https://api.vk.com/method/users.search', params=params)
        result = response.json()
        try:
            if result['response']['count'] != 0:
                res = result['response']['items']
            # Прогресс-бар каждой итерации отображается в терминале
                for item in tqdm(res, desc='Идет поиск...'):

                    profile_url = f"https://vk.com/id{item['id']}"
                    photos = self.get_photos(item['id'])
                    if photos:
                        first_name = item['first_name']
                        last_name = item['last_name']
                        city = self.city
                        # Запись в базу данных при каждой итерации
                        push_pair_data_in_base(
                            self.vk_user_id, first_name, last_name, city, profile_url, photos)
                return 'Всё готово!'
            else:
                raise Exception

        except Exception:
            return f'&#10060; Ошибка:\nОдин или несколько параметров указаны неверно.\nПопробуйте ещё раз.'

    def get_photos(self, user_id):
        '''
        Метод использует API-VK для парсинга фотографий указанного пользователя
        На вход принимает ID пользователя, после чего возвращает 3 популярных (по лайкам) фотографии с профиля
        '''
        photos_params = {'owner_id': user_id,
                         'album_id': 'profile',
                         'rev': '1',
                         'access_token': self.access_token,
                         'extended': '1',
                         'v': '5.131'}
        try:
            photos_response = requests.get(
                'https://api.vk.com/method/photos.get', params=photos_params)
            photos_result = photos_response.json()
            photo_urls = []
            if 'response' in photos_result:
                photos = photos_result['response']['items']
                sorted_photos = sorted(photos, key=lambda x: x.get('likes', {}).get(
                    'count', 0), reverse=True)  # Сортировка по лайкам
                for photo in sorted_photos[:3]:
                    photo_urls.append(photo['sizes'][-1]['url'])
            return photo_urls
        except Exception as e:
            print(f"Ошибка при получении фотографий: {e}")
            return []
