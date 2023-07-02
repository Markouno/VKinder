import requests, json
from tqdm import tqdm
import sys
from sql.SQL_scripts import *


class VK_Parse:
    def __init__(self, access_token, gender, age, city):
        self.access_token = access_token
        self.age = age
        if gender == 'Мужской':
            gender = '2'
        else:
            gender = '1'
        self.gender = gender
        self.city = city

    def parse(self):
        params = {'count': '1000',
                  'sex': self.gender,
                  'hometown': self.city,
                  'age_from': self.age,
                  'age_to': self.age,
                  'has_photo': '1',
                  'access_token': self.access_token,
                  'v': '5.131' 
                  }
        try:
            response = requests.get('https://api.vk.com/method/users.search', params=params)
            result = response.json()
        except Exception as e:
            print(f"Ошибка: {e}")
        else:
            res = result['response']['items']
            for item in tqdm(res, desc='Идет поиск...'):
                profile_url = f"https://vk.com/id{item['id']}"
                photos = self.get_photos(item['id'])
                if photos:
                    first_name = item['first_name']
                    last_name = item['last_name']
                    city = self.city
                    pair_data_push_in_base(first_name, last_name, city, profile_url, photos)

    def get_photos(self, user_id):
        photos_params = {'owner_id': user_id,
                         'album_id': 'profile',
                         'rev': '1',
                         'access_token': self.access_token,
                         'extended': '1',
                         'v': '5.131'}
        try:
            photos_response = requests.get('https://api.vk.com/method/photos.get', params=photos_params)
            photos_result = photos_response.json()
            photo_urls = []
            if 'response' in photos_result:
                photos = photos_result['response']['items']
                sorted_photos = sorted(photos, key=lambda x: x.get('likes', {}).get('count', 0), reverse=True)
                for photo in sorted_photos[:3]:
                    photo_urls.append(photo['sizes'][-1]['url'])
            return photo_urls
        except Exception as e:
            print(f"Ошибка при получении фотографий: {e}")
            return []