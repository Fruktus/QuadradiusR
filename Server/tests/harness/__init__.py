import asyncio
import dataclasses
from abc import ABCMeta
from typing import Callable

import aiohttp
from aiohttp import ClientWebSocketResponse

from quadradiusr_server.config import ServerConfig
from quadradiusr_server.constants import QrwsOpcode
from quadradiusr_server.notification import Handler, Notification
from quadradiusr_server.server import QuadradiusRServer


class RestTestHarness(metaclass=ABCMeta):
    config: ServerConfig
    server: QuadradiusRServer

    async def setup_server(
            self, *, config: ServerConfig = ServerConfig(host='', port=0),
            server_configurator: Callable[[QuadradiusRServer], None] = None) -> None:
        self.config = dataclasses.replace(config)
        self.config.host = '127.0.0.1'
        self.config.port = 0
        self.config.href = 'example.com'
        self.config.database.create_metadata = True
        self.config.auth.scrypt_n = 8
        self.config.auth.scrypt_r = 8
        self.config.auth.scrypt_p = 1
        self.server = QuadradiusRServer(self.config)
        if server_configurator:
            server_configurator(self.server)
        await self.server.start()

    def server_url(self, path: str, *, protocol: str = 'http'):
        return self.server.get_url(protocol) + '/' + path.lstrip('/')

    async def shutdown_server(self):
        await self.server.shutdown()


class TestUserHarness(RestTestHarness, metaclass=ABCMeta):

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
                assert 201 == response.status

    async def authorize_test_user(self, n):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url('/authorize'), json={
                'username': self.get_test_user_username(n),
                'password': self.get_test_user_password(n),
            }) as response:
                assert response.status == 200
                json = await response.json()
                return json['token']

    async def get_test_user(self, n):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/user/@me'), headers={
                'authorization': await self.authorize_test_user(n),
            }) as response:
                return await response.json()

    async def authorize_ws(self, n: int, ws: ClientWebSocketResponse):
        await ws.send_json({
            'op': QrwsOpcode.IDENTIFY,
            'd': {
                'token': await self.authorize_test_user(n),
            },
        })
        data = await ws.receive_json()
        assert QrwsOpcode.SERVER_READY == data['op']


class NotificationHandlerForTests(Handler):
    def __init__(self, topic: str = '*') -> None:
        self.topic = topic
        self.notifications = []

    def get_topic(self):
        return self.topic

    async def handle(self, notification: Notification):
        self.notifications.append(notification)

    @staticmethod
    async def receive_now():
        await asyncio.sleep(0)
