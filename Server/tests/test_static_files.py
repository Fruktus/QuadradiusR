import os
from tempfile import TemporaryDirectory
from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness
from quadradiusr_server.config import ServerConfig


class TestStaticFiles(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        tmp_path = self.temp_dir.name
        os.mkdir(f'{tmp_path}/dir')

        with open(f'{tmp_path}/index.html', 'x') as f:
            f.write('<!doctype html><html><body>test</body></html>')

        with open(f'{tmp_path}/dir/file.txt', 'x') as f:
            f.write('content')

        config = ServerConfig('', 0)
        config.static.serve_path = f'{tmp_path}'
        config.static.redirect_root = '/index.html'
        await self.setup_server(config=config)

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()
        self.temp_dir.cleanup()

    async def test_index(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/index.html')) as response:
                self.assertEqual(200, response.status)
                body = await response.text()
                self.assertEqual('<!doctype html><html><body>test</body></html>', body)
                self.assertEqual('text/html', response.content_type)

    async def test_root(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/')) as response:
                self.assertEqual(200, response.status)
                body = await response.text()
                self.assertEqual('<!doctype html><html><body>test</body></html>', body)
                self.assertEqual('text/html', response.content_type)

    async def test_non_existent(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/non_existent')) as response:
                self.assertEqual(404, response.status)

    async def test_inside_dir(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/dir/file.txt')) as response:
                self.assertEqual(200, response.status)
                body = await response.text()
                self.assertEqual('content', body)
                self.assertEqual('text/plain', response.content_type)
