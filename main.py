import requests, json
from tokens import user_token
from tqdm import tqdm


class VK_Parse:
    def __init__(self, access_token, age_from, age_to, sex):
        self.access_token = access_token
        self.age_from = age_from
        self.age_to = age_to
        self.sex = sex

    def parse(self):
        params = {'count': '1000', 'sex': self.sex, 'age_from': self.age_from, 'age_to': self.age_to, 'access_token': self.access_token, 'v': '5.131'}
        try:
            response = requests.get('https://api.vk.com/method/users.search', params=params)
            result = response.json()
        except Exception as e:
            print(f"Ошибка: {e}")
        else:
            res = result['response']['items']
            json_list = []
            for item in tqdm(res, desc='Идет поиск...'):
                profile_url = f"https://vk.com/id{item['id']}"
                json_list.append({'id': item['id'], 'first_name': item['first_name'], 'last_name': item['last_name'], 'profile_url': profile_url})

                photos = self.get_photos(item['id'])
                json_list[-1]['photos'] = photos

            with open('sql/json_data/pair_data.json', 'w', encoding='UTF-8') as jsonfile:
                json.dump(json_list, jsonfile, ensure_ascii=False, indent=2)

    def get_photos(self, user_id):
        photos_params = {'owner_id': user_id, 'album_id': 'profile', 'rev': '1', 'count': '3', 'access_token': self.access_token, 'v': '5.131'}
        try:
            photos_response = requests.get('https://api.vk.com/method/photos.get', params=photos_params)
            photos_result = photos_response.json()
            photo_urls = []
            if 'response' in photos_result:
                for photo in photos_result['response']['items']:
                    photo_urls.append(photo['sizes'][-1]['url'])
            return photo_urls
        except Exception as e:
            print(f"Ошибка при получении фотографий: {e}")
            return []

# vk_parse = VK_Parse(user_token, 18, 30, 1)
# vk_parse.parse()