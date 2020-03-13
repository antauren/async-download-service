import argparse
from functools import partial

from aiohttp import web
import aiofiles

from handler import archivate

import logging


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def parse_args():
    parser = argparse.ArgumentParser(
        description='''\
        Микросервис для скачивания файлов.
        
        Как запустить: python server.py -p test_photos
        '''
    )

    parser.add_argument('-p', '--path_to_dirs', default='test_photos', help='путь к каталогам с файлами', type=str)
    parser.add_argument('-l', '--logging', default='ERROR', type=str, help='уровень логирования',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('-d', '--delay', default=0, type=int, help='включить задержку ответа')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(level=logging.__dict__[args.logging])

    p_archivate = partial(archivate, dir_path=args.path_to_dirs, delay=args.delay)

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', p_archivate),

    ])
    web.run_app(app)
