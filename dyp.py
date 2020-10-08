import requests
import urllib.request
import os
from tqdm import tqdm
import json

answer = ''
person_id = input('Welcome!\nPlease write your vk_id: ')
token_yandex = input('And token yandex: ')

while True:
    menu = input('If you want create folder in your pc write "cf"\n'
                 'upload to yandex from vk use "vkyandex"\n'
                 'to exit use "exit": ').lower()
    if menu == 'exit':
        break
    elif menu == 'cf':

        def createfolder(folder_name, path):
            '''
            Create folder in your pc
            return path to folder
            '''
            if not (os.path.exists(path + '/' + folder_name)):
                os.chdir(path)
                os.mkdir(folder_name)
                print(f"Folder with name {folder_name} created. Path to folder is: {path + '/' + folder_name}")
                return f"{path + '/' + folder_name}"
            else:
                print(f"Folder with name {folder_name} already created. Path to folder is: {path + '/' + folder_name}")
                return f"{path + '/' + folder_name}"


        path = createfolder(input('Write name of folder: '), input('Write path: '))
        while True:
            answer = input('Will you use this path to save img from site?\n"yes" or "no": ').lower()
            if answer == 'yes' or answer == 'no':
                break
    elif menu == 'vkyandex':
        def req(person_id, number_of_photos, token_vk):
            '''
            This func do requests into page of person and get photos from his profile with the largest size
            return dict of url,date_uploading : likes
            '''
            url_and_likes = {}
            size = {}
            response = requests.get(
                'https://api.vk.com/method/photos.get',
                params={
                    'access_token': token_vk,
                    'owner_id': person_id,
                    'album_id': 'profile',
                    'extended': 1,
                    'feed_type': 'photo',
                    'photo_size': 1,
                    'count': number_of_photos,
                    'v': 5.122
                })
            for cycle in range(0, number_of_photos):
                response_json = response.json()['response']['items'][cycle]['sizes']
                for list_with_params in range(0, (len(response_json))):
                    size[response_json[list_with_params]['height']] = response_json[list_with_params]['url']
                max_ = max(size.keys())
                url_and_likes[size[max_], response.json()['response']['items'][cycle]['date']] = {
                    'Likes': response.json()['response']['items'][cycle]['likes']['count']}
            return url_and_likes


        url_and_likes = req(person_id, 5,
                            '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008')


        def folderwithphotos(path=''):
            '''
            Download files from site to folder
            return path to folder and list with names of img
            '''
            list_of_name = []
            if answer == 'no' or answer == '':
                path = input('Write your path to folder where will be img: ')
            previosly_likes = ''
            for url, date in url_and_likes.items():
                if date['Likes'] == previosly_likes:
                    urllib.request.urlretrieve(url[0],
                                               os.path.join(path, os.path.basename(f'{date["Likes"]}{url[1]}.jpg')))
                    list_of_name.append(f'{date["Likes"]}{url[1]}.jpg')
                    continue
                urllib.request.urlretrieve(url[0], os.path.join(path, os.path.basename(f'{date["Likes"]}.jpg')))
                list_of_name.append(f'{date["Likes"]}.jpg')
                previosly_likes = date['Likes']
            if answer == 'no' or answer == '':
                return path, list_of_name
            elif answer == 'yes':
                return list_of_name


        if answer == 'no' or answer == '':
            path, list_of_name = folderwithphotos()
        elif answer == 'yes':
            list_of_name = folderwithphotos(path)


        def uploadtoyandex(token_yandex, my_path):
            '''
            This func upload your img to folder in yandex disk and return info about img
            '''
            foldername = input('Write folder name which will be created in yandex disk: ')
            create_folder = requests.put(
                f'https://cloud-api.yandex.net/v1/disk/resources?path={foldername}',
                headers={"Authorization": f"{token_yandex}"})
            print(f'File with name {foldername} created')
            for i in tqdm(list_of_name):
                path_to_file = f'/{i}'
                with open(f'{my_path}{path_to_file}', 'rb') as f:
                    with open('jsoninfo.json', 'a') as j:
                        resp_get = requests.get(
                            f'https://cloud-api.yandex.net/v1/disk/resources/upload/?path={foldername}{path_to_file}&overwrite=true',
                            headers={"Authorization": f"{token_yandex}"})
                        resp_put = requests.put(resp_get.json()['href'], files={'file': f})
                        response_get_info = requests.get(
                            f'https://cloud-api.yandex.net/v1/disk/resources?path=/{foldername}{path_to_file}&fields=name,size',
                            headers={"Authorization": f"{token_yandex}"})
                        json.dump(response_get_info.json(), j, sort_keys=True, indent=2)
            print(open('jsoninfo.json').read())
            open('jsoninfo.json', 'w').close()


        uploadtoyandex(token_yandex, path)
