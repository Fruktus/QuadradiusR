import base64
import json
from dataclasses import dataclass
from typing import Dict, Tuple

import jsondiff as jsondiff

from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Game, clone_db_object
from quadradiusr_server.db.base import User
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import BasicConnection, QrwsConnection
from quadradiusr_server.qrws_messages import Message, KickMessage, GameStateMessage


@dataclass
class Tile:
    elevation: int

    def serialize_for(self, user: User):
        return {
            'elevation': self.elevation,
        }


@dataclass
class GameSettings:
    board_size: Tuple[int, int]

    def serialize_for(self, user: User):
        return {
            'board_size': [
                self.board_size[0],
                self.board_size[1],
            ]
        }


@dataclass
class GameBoard:
    tiles: Dict[Tuple[int, int], Tile]

    def serialize_for(self, user: User):
        return {
            'tiles': [
                {
                    'x': pos[0],
                    'y': pos[1],
                    'tile': tile.serialize_for(user),
                } for pos, tile in self.tiles.items()
            ],
        }


@dataclass
class GameState:
    settings: GameSettings
    board: GameBoard

    def serialize_for(self, user: User) -> dict:
        return {
            'settings': self.settings.serialize_for(user),
            'board': self.board.serialize_for(user),
        }

    def serialize_with_etag_for(self, user: User) -> Tuple[dict, str]:
        serialized = self.serialize_for(user)
        hash_int = hash(json.dumps(serialized))
        hash_bytes = hash_int.to_bytes(
            (hash_int.bit_length() + 7) // 8,
            byteorder='big', signed=True)
        hash_str = base64.b85encode(hash_bytes).decode()
        return serialized, hash_str

    @staticmethod
    def serialize_diff_with_etag_for(
            from_: 'GameState',
            to: 'GameState',
            user: User) -> Tuple[dict, str, str]:
        from_serialized, from_etag = from_.serialize_with_etag_for(user)
        to_serialized, to_etag = to.serialize_with_etag_for(user)

        return jsondiff.diff(from_, to), from_etag, to_etag

    @classmethod
    def initial(cls):
        board_size = (10, 8)
        return GameState(
            settings=GameSettings(
                board_size=board_size,
            ),
            board=GameBoard(
                tiles={
                    (x, y): Tile(elevation=0)
                    for x in range(board_size[0])
                    for y in range(board_size[1])
                },
            ),
        )


class GameInProgress:
    def __init__(self, game: Game, repository: Repository) -> None:
        self.game = clone_db_object(game)
        self.repository = repository

        self.player_a_connection: GameConnection | None = None
        self.player_b_connection: GameConnection | None = None

    @property
    def game_state(self) -> GameState:
        return self.game.game_state_

    def is_player_connected(self, player_id):
        if self.game.player_a_id_ == player_id:
            return self.player_a_connection is not None
        if self.game.player_b_id_ == player_id:
            return self.player_b_connection is not None
        return False

    async def connect_player(self, connection: 'GameConnection'):
        if self.game.player_a_id_ == connection.user.id_:
            if self.player_a_connection:
                await self.player_a_connection.kick()
            self.player_a_connection = connection
        elif self.game.player_b_id_ == connection.user.id_:
            if self.player_b_connection:
                await self.player_b_connection.kick()
            self.player_b_connection = connection
        else:
            raise ValueError(
                f'User {connection.user} is not part of the game {self.game}')

    async def disconnect_player(self, connection: 'GameConnection'):
        if self.player_a_connection == connection:
            self.player_a_connection = None
        if self.player_b_connection == connection:
            self.player_b_connection = None

    def save(self):
        import asyncio
        asyncio.create_task(self.save_now())

    async def save_now(self):
        await self.repository.game_repository.save(clone_db_object(self.game))


class GameConnection(BasicConnection):

    def __init__(
            self, qrws: QrwsConnection,
            game_in_progress: GameInProgress,
            user: User,
            notification_service: NotificationService,
            database: DatabaseEngine) -> None:
        super().__init__(qrws, user, notification_service, database)
        self.game_in_progress = game_in_progress

    async def on_ready(self):
        game_state = self.game_in_progress.game_state
        serialized, etag = game_state.serialize_with_etag_for(self.user)
        await self.qrws.send_message(
            GameStateMessage(game_state=serialized, etag=etag))

    async def handle_message(self, message: Message) -> bool:
        if await super().handle_message(message):
            return True

        return False

    async def kick(self):
        await self.qrws.send_message(KickMessage(
            reason='Connected from another location',
        ))
        await self.qrws.close(
            QrwsCloseCode.CONFLICT,
            'Connected from another location')
