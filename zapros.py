import json
import requests
from token import token_vk
import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from token_1 import community_token
from token_1 import user_token


class VK:
    URL = 'https://api.vk.com/method/'
    vk_session = vk_api.VkApi(token=community_token)
    bot = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
    def __init__(self, access_token=None, version=None):
        self.access_token = access_token
        self.version = version
    
    def get_info(self, user_ids=None, screen_names=None):
        if user_ids is None and screen_names is None:
            return None
        if user_ids:
            method = 'users.get'
            params = {
                'user_ids': user_ids,
            }
        else:
            method = 'users.get'
            params = {
                'user_ids': screen_names,
                'user_id_type': 'screen_name',
            }
        url = self.URL + method
        params.update({
            'access_token': self.access_token,
            'fields': 'screen_name, city, bdate, sex',
            'v': self.version
        })
        
        res = self.get_data(url, params)
        response = res.json().get("response")
        
        if response:
            return response[0]
        else:
            return None
        
    def photos_get(self, owner_id: str, count=3):
        method = 'photos.get'
        url = self.URL + method
        params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'access_token': self.access_token,
            'extended': 1,
            'count': count,
            'v': self.version
        }
        res = self.get_data(url, params)
        res = res.json()

        if res.get('error') is not None:
            print(res['error']['error_msg'])
        else:
            photo_links = []
            if res['response']['items']:
                for item in res['response']['items']:
                    photo_links.append(f"photo{item['owner_id']}_{item['id']}")
            return photo_links
        return res
    
    @staticmethod
    def get_data(url, params):
        iteration = True
        while iteration:
            resp = requests.get(url, params=params)
            data = resp.json()
            if 'error' in data and 'error_code' in data['error'] and data['error']['error_code'] == 6:
                time.sleep(2)
            else:
                iteration = False
        return resp
    
    @staticmethod
    def get_sex(sex):
        if sex == 1:
            sex = 2
        elif sex == 2:
            sex = 1
        else:
            sex = 0
        return sex
    
    def get_search_user(self, count=1, offset=0):
        method = 'users.search'
        url = self.URL + method
        access_token = self.access_token
        params = dict(count=count, offset=offset, city=1, 
                      age_to=30, sex=self.get_sex, access_token=access_token, v='5.131', has_photo=1)
        res = self.get_data(url, params)
        print(res.json())
        response = res.json().get("response")
        list_user = []
        for i in response.get('items'):
            if i.get("can_access_closed"):
                list_user.append(i.get("id"))
        return list_user
    
    def send_user_info(self, peer_id, user_info):
        message = f"Имя: {user_info['first_name']}\nФамилия: {user_info['last_name']}\n" \
                f"Ссылка на профиль: https://vk.com/id{user_info['id']}"
        photo_links = self.photos_get(user_info['id'])
        if photo_links:
            photos = ','.join(photo_links)
            self.bot.messages.send(peer_id=peer_id, message=message, attachment=photos)
        else:
            self.bot.messages.send(peer_id=peer_id, message=message)