import argparse
from functools import partial

from aiohttp import web
import aiofiles

from handler import archivate


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
    parser.add_argument('-l', '--logging', default=False, type=bool, help='включить логирование', choices=[True, False])
    parser.add_argument('-d', '--delay', default=0, type=int, help='включить задержку ответа')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    p_archivate = partial(archivate, dir_path=args.path_to_dirs, delay=args.delay, log=args.logging)

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', p_archivate),

    ])
    web.run_app(app)
