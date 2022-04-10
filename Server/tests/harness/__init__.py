import asyncio
import dataclasses
import uuid
from abc import ABCMeta
from datetime import datetime, timedelta, timezone
from typing import Callable

import aiohttp
from aiohttp import ClientWebSocketResponse

from quadradiusr_server.config import ServerConfig
from quadradiusr_server.constants import QrwsOpcode
from quadradiusr_server.db.base import Game
from quadradiusr_server.db.transactions import transaction_context
from quadradiusr_server.game import GameState
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


# noinspection PyMethodMayBeStatic
class WebsocketHarness(metaclass=ABCMeta):
    async def ws_subscribe(self, ws: ClientWebSocketResponse, topic: str):
        await ws.send_json({
            'op': QrwsOpcode.SUBSCRIBE,
            'd': {
                'topic': topic,
            },
        })
        data = await ws.receive_json()
        assert QrwsOpcode.SUBSCRIBED == data['op']

    async def ws_receive_notification(self, ws: ClientWebSocketResponse):
        data = await ws.receive_json()
        assert QrwsOpcode.NOTIFICATION == data['op']
        return data['d']


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


class GameHarness(RestTestHarness, metaclass=ABCMeta):
    async def create_game(self, player_a_id: str, player_b_id: str) -> str:
        assert player_a_id != player_b_id
        async with transaction_context(self.server.database):
            game_state = GameState.initial(player_a_id, player_b_id)
            game_id = str(uuid.uuid4())
            game = Game(
                id_=game_id,
                player_a_id_=player_a_id,
                player_b_id_=player_b_id,
                expires_at_=datetime.now(timezone.utc) + timedelta(minutes=10),
                game_state_=game_state,
            )
            await self.server.repository.game_repository.add(game)
            return game_id

    async def get_game_state(self, game_id: str) -> GameState:
        async with transaction_context(self.server.database):
            game = await self.server.repository.game_repository.get_by_id(game_id)
            return game.game_state_

    async def set_game_state(self, game_id: str, game_state: GameState):
        async with transaction_context(self.server.database):
            game = await self.server.repository.game_repository.get_by_id(game_id)
            game.game_state_ = game_state


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
