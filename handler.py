import os

import asyncio
from aiohttp import web
from aiohttp.web import HTTPNotFound

import logging

logger = logging.getLogger(__file__)


async def archivate(request, dir_path, delay=0):
    if os.path.samefile(dir_path, '.') or os.path.samefile(dir_path, '..'):
        raise HTTPNotFound(reason='путь не должен вести на ".." или "."')

    if not os.path.exists(dir_path):
        raise HTTPNotFound(reason='Архив не существует или был удален')

    archive_hash = request.match_info['archive_hash']
    dir_path = os.path.join(dir_path, archive_hash)

    cmd = ['zip', '-r', '-', dir_path]

    response = web.StreamResponse()

    response.headers['Content-Disposition'] = 'attachment; filename="archive.zip"'

    await response.prepare(request)

    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    try:
        while True:
            archive_chunk = await proc.stdout.readline()

            logger.debug('Sending archive chunk ...')

            if not archive_chunk:
                break

            await response.write(archive_chunk)

            if delay > 0:
                await asyncio.sleep(delay)

    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError, RuntimeError):
        logger.warning('Download was interrupted.')

        raise KeyboardInterrupt

    finally:
        proc.kill()

        response.force_close()

    return response
