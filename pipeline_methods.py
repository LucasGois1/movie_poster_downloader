import asyncio
import os
from asyncio import Semaphore
from collections import Counter
from http import HTTPStatus

import aiohttp
import tqdm
from aiofile import async_open
from aiohttp.http_exceptions import HttpProcessingError
from aiohttp.web_exceptions import HTTPNotFound

from exceptions.FetchError import FetchError
from models.Movie import Movie
from tools.Result import Result

BASE_URL_INFORMATION = 'https://api.themoviedb.org/3'
BASE_URL_IMAGES = 'https://image.tmdb.org/t/p'
API_KEY = 'e4c1d8c4900313ad3b59fc87cd377bf6'
LANGUAGE = 'pt_BR'
DEST_DIR = '/Users/lucasgois/Desktop/movie_images'


async def save_image(img_bytes: bytes, filename: str, file_format: str = 'jpg'):
    path = os.path.join(DEST_DIR, f'{filename}.{file_format}')

    async with async_open(path, 'wb') as file:
        await file.write(img_bytes)


async def get_movie(movie_id: int, semaphore: Semaphore):
    url = f'{BASE_URL_INFORMATION}/movie/{movie_id}?api_key={API_KEY}&language={LANGUAGE}'

    async with aiohttp.ClientSession() as session:
        async with semaphore, session.get(url) as response:

            if response.status == 200:
                content = await response.json()
                return Movie(
                    id=content['id'],
                    name=content['belongs_to_collection']['name'].replace('/', '-'),
                    poster_path=content['belongs_to_collection']['poster_path'][1:]
                )

            if response.status == 404:
                raise HTTPNotFound()

            else:
                raise HttpProcessingError()


async def get_poster(poster_path: str, width: int, semaphore: Semaphore):
    url = f'{BASE_URL_IMAGES}/w{width}/{poster_path}'

    async with aiohttp.ClientSession() as session:
        async with semaphore, session.get(url) as response:
            if response.status == 200:
                poster = await response.read()
                return poster

            if response.status == 404:
                raise HTTPNotFound()

            else:
                raise HttpProcessingError()


async def pipeline(movie_id: int, semaphore: Semaphore):
    try:
        filme = await get_movie(movie_id, semaphore)
        filme['poster_bytes'] = await get_poster(filme['poster_path'], 1080, semaphore)

    except HTTPNotFound:
        status, msg = HTTPStatus.NOT_FOUND, 'Filme não encontrado.'

    except Exception as exc:
        raise FetchError(f'ID: {movie_id}') from exc

    else:
        await save_image(filme['poster_bytes'], filme['name'])

        status, msg = HTTPStatus.OK, 'Download finalizado de {filme}'.format(filme=filme['name'])

    return Result(status, msg)


async def get_content(init, end):
    counter = Counter()
    semaphore = Semaphore(5)
    to_do = [pipeline(movie_id, semaphore) for movie_id in range(init, end)]

    tasks = asyncio.as_completed(to_do)
    tasks = tqdm.tqdm(tasks, desc="Concluído", total=end - init, colour='#ffff00')

    for future in tasks:
        try:
            response = await future

        except FetchError:
            status = HTTPStatus.INTERNAL_SERVER_ERROR

        else:
            status = response.status
            tasks.set_postfix_str(response.msg)

        counter[status] += 1

    return counter
