import dataclasses
import re
from abc import ABCMeta

import aiohttp

from quadradiusr_server.auth import hash_password
from quadradiusr_server.config import ServerConfig
from quadradiusr_server.db.base import User
from quadradiusr_server.server import QuadradiusRServer


class RestTestHarness(metaclass=ABCMeta):
    config: ServerConfig
    server: QuadradiusRServer

    async def setup_server(self, config: ServerConfig = ServerConfig(host='', port=0)) -> None:
        self.config = dataclasses.replace(config)
        self.config.host = '127.0.0.1'
        self.config.port = 0
        self.config.database.create_metadata = True
        self.server = QuadradiusRServer(self.config)
        await self.server.start()

    def server_url(self, path: str, *, protocol: str = 'http'):
        return self.server.get_url(protocol) + '/' + path.lstrip('/')

    async def shutdown_server(self):
        await self.server.shutdown()


class TestUserHarness(RestTestHarness, metaclass=ABCMeta):
    __user: User = None

    def get_test_user_username(self, n):
        return f'test_user_{n}'

    def get_test_user_password(self, n):
        return f'test_password_{n}'

    async def create_test_user(self, n):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url('/user'), json={
                'username': self.get_test_user_username(n),
                'password': self.get_test_user_password(n),
            }) as response:
                self.assertEqual(201, response.status)

    async def authorize_test_user(self, n):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url('/authorize'), json={
                'username': self.get_test_user_username(n),
                'password': self.get_test_user_password(n),
            }) as response:
                json = await response.json()
                return json['token']

    async def get_test_user(self, n):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/user/@me'), headers={
                'authorization': await self.authorize_test_user(n),
            }) as response:
                return await response.json()
