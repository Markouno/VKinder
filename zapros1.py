import json
import requests

class VKApi:
    def __init__(self, access_token):
        self.access_token = access_token
        self.URL = 'https://api.vk.com/method/'
        self.version = '5.131'

    def get_data(self, url, params):
        res = requests.get(url, params=params)
        return res
    
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

    def users_get(self, user_id):
        method = "users.get"
        url = self.URL + method
        params = {
            "access_token": self.access_token,
            "user_ids": user_id,
            "fields": "photo_max,screen_name",
            "v": self.version
        }
        res = self.get_data(url, params)
        res = res.json()

        if res.get('error') is not None:
            print(res['error']['error_msg'])
        else:
            user_info = {}
            if res['response']:
                user = res['response'][0]
                user_info = {
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "profile_url": f"https://vk.com/{user['screen_name']}",
                }
            return user_info

    def get_photos_and_users(self, owner_id: str, count=3):
        photo_links = self.photos_get(owner_id, count)
        user_id = owner_id
        user_info = self.users_get(user_id)

        attachments = []
        for photo_link in photo_links:
            method = "photos.getById"
            url = self.URL + method
            params = {
                "access_token": self.access_token,
                "photos": photo_link,
                "v": self.version
            }
            res = self.get_data(url, params)
            res = res.json()

            if res.get('error') is not None:
                print(res['error']['error_msg'])
            else:
                if res['response']:
                    photo = res['response'][0]
                    attachment = f"photo{photo['owner_id']}_{photo['id']}"
                    attachments.append(attachment)
                    if len(attachments)==count:
                        break
        if len(attachments) < count:
            attachments += [None] * (count - len(attachments))
        data = {"owner_id": owner_id, "user_info": user_info, "attachments": attachments[:count]}
        return data


if __name__ == '__main__':
    access_token = "vk1.a.BURzlCYTeOf8oQguF0orWjJwKmsFq-JIwAXbltgbv6yCuAzOsulHsm5109BzzJP9wmVi77Fd9q-ZDIStHCrlc19wsdhVn2mSiB7A88RzVistvlUJ7-NBPY-HfFhBTb4awc69VcvfI6Txxr2O7Krb1XUjjhB2vuUKXXF5GQJTe2WHVovxvLEZdk5H4cQtk36U6QI4G5BJhsH-ckQcnwF0yg"
    api = VKApi(access_token)
    data = api.get_photos_and_users(owner_id="473860275", count=3)
    with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)