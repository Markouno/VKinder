import requests
import json
from tokens import user_token


class VK_Parse:
    def __init__(self, access_token, age_from, age_to, sex):
        self.access_token = access_token
        self.age_from = age_from
        self.age_to = age_to
        self.sex = sex

    def parse(self):
        params = {'count': '1000', 'sex': self.sex, 'has_photo': '1', 'age_from': self.age_from, 'age_to': self.age_to, 'access_token': self.access_token, 'v': '5.131', 'fields': 'city'}
        try:
            response = requests.get('https://api.vk.com/method/users.search', params=params)
            result = response.json()
        except Exception as e:
            print(f"Ошибка: {e}")
        else:
            res = result['response']['items']
            json_list = []
            for item in res:
                profile_url = f"https://vk.com/id{item['id']}"
                photos = self.get_photos(item['id'])
                city = item.get('city', {}).get('title')
                if city and photos:
                    json_list.append({'id': item['id'], 'first_name': item['first_name'], 'last_name': item['last_name'], 'city': city, 'profile_url': profile_url, 'photos': photos})

            with open('pair_data.json', 'w', encoding='UTF-8') as jsonfile:
                json.dump(json_list, jsonfile, ensure_ascii=False, indent=2)

    def get_photos(self, user_id):
        photos_params = {'owner_id': user_id, 'album_id': 'profile', 'rev': '1', 'count': '3', 'access_token': self.access_token, 'v': '5.131'}
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

vk_parse = VK_Parse(user_token, 18, 30, 1)
vk_parse.parse()