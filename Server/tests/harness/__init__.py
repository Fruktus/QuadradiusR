import asyncio
import dataclasses
import uuid
from abc import ABCMeta
from datetime import datetime, timedelta, timezone
from typing import Callable, Tuple, List, Optional
from unittest import TestCase

import aiohttp
from aiohttp import ClientWebSocketResponse

from quadradiusr_server.config import ServerConfig
from quadradiusr_server.constants import QrwsOpcode
from quadradiusr_server.db.base import Game
from quadradiusr_server.db.transactions import transaction_context
from quadradiusr_server.game_state import GameState, Power
from quadradiusr_server.notification import Handler, Notification
from quadradiusr_server.powers import PowerRandomizer, PowerDefinition
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
        self.config.game.power_randomizer_class = 'harness.PowerRandomizerForTests'
        self.server = QuadradiusRServer(self.config)
        if server_configurator:
            server_configurator(self.server)
        await self.server.start()

    def server_url(self, path: str, *, protocol: str = 'http'):
        return self.server.get_url(protocol) + '/' + path.lstrip('/')

    async def shutdown_server(self):
        await self.server.shutdown()


# noinspection PyMethodMayBeStatic
class WebsocketHarness(TestCase, metaclass=ABCMeta):
    async def ws_subscribe(self, ws: ClientWebSocketResponse, topic: str):
        await ws.send_json({
            'op': QrwsOpcode.SUBSCRIBE,
            'd': {
                'topic': topic,
            },
        })
        data = await ws.receive_json()
        self.assertEqual(QrwsOpcode.SUBSCRIBED, data['op'])

    async def ws_receive_notification(self, ws: ClientWebSocketResponse):
        data = await ws.receive_json()
        self.assertEqual(QrwsOpcode.NOTIFICATION, data['op'])
        return data['d']

    async def ws_move(
            self, ws: ClientWebSocketResponse,
            piece_id: str, tile_id: str):
        await ws.send_json({
            'op': 11,
            'd': {
                'piece_id': piece_id,
                'tile_id': tile_id,
            }
        })

    async def ws_apply_power(
            self, ws: ClientWebSocketResponse,
            power_id: str):
        await ws.send_json({
            'op': 13,
            'd': {
                'power_id': power_id,
            }
        })

    async def ws_send_message(
            self, ws: ClientWebSocketResponse,
            content: str,
            wait_for_notification: bool = False):
        await ws.send_json({
            'op': QrwsOpcode.SEND_MESSAGE,
            'd': {
                'content': content,
            },
        })

        if wait_for_notification:
            while True:
                n = await self.ws_receive_notification(ws)
                if n['topic'] == 'lobby.message.received' and \
                        n['data']['message']['content'] == content:
                    return

    async def ws_receive(self, ws: ClientWebSocketResponse, op: int):
        while True:
            msg = await ws.receive_json()
            if msg['op'] == op:
                return msg


class TestUserHarness(RestTestHarness, TestCase, metaclass=ABCMeta):

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
                self.assertEqual(200, response.status)
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
        self.assertEqual(QrwsOpcode.SERVER_READY, data['op'])


class GameHarness(TestUserHarness, metaclass=ABCMeta):
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

    async def query_game_state(self, user_no: int, game_id: str) -> GameState:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url(f'/game/{game_id}/state'), headers={
                'authorization': await self.authorize_test_user(user_no),
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertIsNotNone(body)
                return body

    def get_game_tile_id_at(
            self, game_state: any,
            xy: Tuple[int, int]) -> str:
        x, y = xy
        tiles = game_state['board']['tiles']

        the_tile_id = None
        for tile_id, tile in tiles.items():
            pos = tile['position']
            if pos['x'] == x and pos['y'] == y:
                if the_tile_id is not None:
                    raise AssertionError(f'Duplicate tile at ({x}, {y}): {game_state}')
                the_tile_id = tile_id
        if the_tile_id is None:
            raise AssertionError(f'No tile at ({x}, {y}): {game_state}')

        return the_tile_id

    def get_game_piece_id_at(
            self, game_state: any,
            xy: Tuple[int, int]):
        x, y = xy
        tile_id = self.get_game_tile_id_at(game_state, xy)
        pieces = game_state['board']['pieces']

        the_piece_id = None
        for piece_id, piece in pieces.items():
            if piece['tile_id'] == tile_id:
                if the_piece_id is not None:
                    raise AssertionError(f'Duplicate piece at ({x}, {y}): {game_state}')
                the_piece_id = piece_id
        if the_piece_id is None:
            raise AssertionError(f'No piece at ({x}, {y}): {game_state}')

        return the_piece_id


class NotificationHandlerForTests(Handler):
    def __init__(self) -> None:
        self.notifications = []

    async def handle(self, notification: Notification):
        self.notifications.append(notification)

    @staticmethod
    async def receive_now():
        await asyncio.sleep(0)


class PowerRandomizerForTests(PowerRandomizer):
    power_to_spawn: Optional[Power] = None

    def after_move(
            self,
            game_state: GameState,
            power_definitions: List[PowerDefinition]) -> None:
        if self.power_to_spawn:
            game_state.board.powers[self.power_to_spawn.id] = self.power_to_spawn
            self.power_to_spawn = None

    @classmethod
    def spawn_next_power(cls, power_to_spawn: Power):
        cls.power_to_spawn = power_to_spawn
