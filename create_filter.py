import json


def create_filter(f_list):
    '''
    Данный метод принимает список параметров для поиска,
    после чего конвертирует их в JSON-файл.

    '''
    gender, age, city = f_list[0], f_list[1], f_list[2]
    
    user_dict = {'gender': gender,
                 'age': age,
                 'city': city 
    }

    with open('sql/json_data/user_data.json', 'w', encoding='UTF-8') as jsonfile:
        json.dump(user_dict, jsonfile, indent=2, ensure_ascii=False)
