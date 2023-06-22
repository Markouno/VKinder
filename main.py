import requests
from pprint import pprint
from tokens import community_token
from tokens import user_token
import json



def parse():
    params = {'count': '1000', 'sex': '1', 'age_to': '26', 'access_token': user_token, 'v': '5.131'}
    response = requests.get('https://api.vk.com/method/users.search', params=params)
    result = response.json()
    some_shit = result['response']['items']
    json_list = []
    count = 0
    for item in some_shit:
        json_list.append(item['id'])
        count += 1

    with open('data.json', 'a', encoding='UTF-8') as jsonfile:
        json.dump(json_list, jsonfile, indent= 2)
    return result, count

def get_mod():
    my_list = parse()
    person = my_list['response']['items']
    for item in person:
        id = item['id']
        params = {'owner_id': id, 'album_id': 'profile', 'extended': '1','access_token': user_token, 'v': '5.131'}
        response = requests.get(f'https://api.vk.com/method/photos.get', params=params)
        result = response.json()
        # max_pic_size = sorted(item['sizes'], key=lambda x: (x['width'], x['height']))[-1]
        return result


if __name__ == '__main__':
    pprint(parse())
    # pprint(get_mod())
