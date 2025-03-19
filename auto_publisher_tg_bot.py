import os.path
import random
from pathlib import Path

import requests
import telegram
from environs import Env


def get_comics_quantity():
    comics_url = 'https://xkcd.com/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()
    decoded_comics_data = response.json()
    return decoded_comics_data['num']


def download_image(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(os.path.join(path, 'comics_photo'), 'wb') as file:
        file.write(response.content)


def get_comics_data(number):
    comics_url = f'https://xkcd.com/{number}/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()
    decoded_comics_data = response.json()
    return decoded_comics_data


def main():
    env = Env()
    env.read_env()
    bot = telegram.Bot(token=env('TG_API_KEY'))
    chat_id = env('CHAT_ID')
    path_to_images = 'images'

    Path(path_to_images).mkdir(parents=True, exist_ok=True)
    quantity_of_comics = get_comics_quantity()
    random_comics = random.randint(1, quantity_of_comics)
    comics_data = get_comics_data(random_comics)
    try:
        download_image(comics_data['img'], path_to_images)
        with open(os.path.join(path_to_images, 'comics_photo'), 'rb') as file:
            bot.send_photo(chat_id=chat_id, photo=file, caption=comics_data['alt'])
    finally:
        os.remove(os.path.join(path_to_images, 'comics_photo'))


if __name__ == '__main__':
    main()
