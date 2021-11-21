import asyncio
import os
from collections import Counter, namedtuple
from http import HTTPStatus
from typing import TypedDict

import aiohttp
import tqdm
from aiohttp.http_exceptions import HttpProcessingError
from aiohttp.web_exceptions import HTTPNotFound

BASE_URL_INFORMATION = 'https://api.themoviedb.org/3'
BASE_URL_IMAGES = 'https://image.tmdb.org/t/p'
API_KEY = 'e4c1d8c4900313ad3b59fc87cd377bf6'
LANGUAGE = 'pt_BR'

DEST_DIR = '/Users/lucasgois/Desktop/movie_images'


def save_image(img_bytes: bytes, filename: str, file_format: str = 'jpg'):
    path = os.path.join(DEST_DIR, f'{filename}.{file_format}')

    with open(path, 'wb') as file:
        file.write(img_bytes)


Result = namedtuple('Result', 'status msg')


class Movie(TypedDict, total=False):
    id: int
    name: str
    poster_path: str
    poster_bytes: bytes


class FetchError(Exception):
    def __init__(self, message: str):
        self.message = f'Houve um problema durante a requisição. {message}'


async def get_movie(movie_id: int):
    url = f'{BASE_URL_INFORMATION}/movie/{movie_id}?api_key={API_KEY}&language={LANGUAGE}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.json()
                return Movie(
                    id=content['id'],
                    name=content['belongs_to_collection']['name'],
                    poster_path=content['belongs_to_collection']['poster_path'].replace('/', '-')[1:]
                )

            if response.status == 404:
                raise HTTPNotFound()

            else:
                raise HttpProcessingError()


async def get_poster(poster_path: str, width: int):
    url = f'{BASE_URL_IMAGES}/w{width}/{poster_path}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                poster = await response.read()
                return poster

            if response.status == 404:
                raise HTTPNotFound()

            else:
                raise HttpProcessingError()


async def download_one(movie_id: int):
    try:
        filme = await get_movie(movie_id)
        filme['poster_bytes'] = await get_poster(poster_path=filme['poster_path'], width=500)

    except HTTPNotFound:
        status = HTTPStatus.NOT_FOUND
        msg = 'Filme não encontrado.'

    except Exception as exc:
        raise FetchError(f'ID: {movie_id}') from exc

    else:
        save_image(filme['poster_bytes'], filme['name'])

        status = HTTPStatus.OK
        msg = 'OK'

    return Result(status, msg)


async def corrotina(init, end):
    counter = Counter()
    to_do = [download_one(movie_id) for movie_id in range(init, end)]

    tasks = asyncio.as_completed(to_do)

    tasks = tqdm.tqdm(tasks, total=end - init, colour='#0000ff')

    for future in tasks:
        try:
            response = await future

        except FetchError:
            status = HTTPStatus.INTERNAL_SERVER_ERROR

        else:
            status = response.status

        counter[status] += 1

    return counter


def download_movie_images():
    loop = asyncio.get_event_loop()
    download_pipeline = corrotina(1, 10000)
    counts = loop.run_until_complete(download_pipeline)
    loop.close()

    return counts


if __name__ == '__main__':
    print(download_movie_images())
