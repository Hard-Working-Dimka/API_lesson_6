import argparse
import os.path
import time
import random
from pathlib import Path

import requests
import telegram
from environs import Env
import configargparse
from pytimeparse import parse


def get_comics_quantity():
    comics_url = 'https://xkcd.com/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()
    decoded_comics_data = response.json()
    return decoded_comics_data['num']


def download_image(url, path):
    Path(path).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    with open(os.path.join(path, 'comics_photo'), 'wb') as file:
        file.write(response.content)


def remove_image(path):
    os.remove(os.path.join(path, 'comics_photo'))


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

    command_line_parser = configargparse.ArgumentParser(
        description='Запуск ТГ бота для выкладывания картинок'
    )
    command_line_parser.add_argument('-p', '--path', default='images', env_var='PATH_TO_IMAGES',
                                     help='Путь загрузки фотографий')
    command_line_parser.add_argument('-per', '--publication_period', default='4h',
                                     env_var='PUBLICATION_PERIOD', help='Период отправки фотографий')
    command_line_parser.add_argument('--once', default=False, help='Запуск программы разово',
                                     action=argparse.BooleanOptionalAction)

    args = command_line_parser.parse_args()

    while True:
        quantity_of_comics = get_comics_quantity()
        random_comics = random.randint(1, quantity_of_comics)
        comics_data = get_comics_data(random_comics)
        download_image(comics_data['img'], args.path)

        with open(os.path.join(args.path, 'comics_photo'), 'rb') as file:
            bot.send_photo(chat_id=chat_id, photo=file, caption=comics_data['alt'])
        remove_image(args.path)
        time.sleep(parse(args.publication_period))

        if args.once:
            break


if __name__ == '__main__':
    main()
