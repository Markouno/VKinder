import requests
from pprint import pprint
from token_ import TOKEN
from token_ import vk_token



def parse():
    params = {'count': '10', 'sex': '2', 'age_to': '26', 'access_token': vk_token, 'v': '5.131'}
    response = requests.get('https://api.vk.com/method/users.search', params=params)
    result = response.json()
    return result

def get_mod():
    my_list = parse()
    person = my_list['response']['items']
    for item in person:
        id = item['id']
        params = {'owner_id': id, 'album_id': 'profile', 'extended': '1','access_token': vk_token, 'v': '5.131'}
        response = requests.get(f'https://api.vk.com/method/photos.get', params=params)
        result = response.json()
        return result



if __name__ == '__main__':
    # pprint(parse())
    pprint(get_mod())