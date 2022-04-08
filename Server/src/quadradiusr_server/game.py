from dataclasses import dataclass
from typing import Dict, Tuple

from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Game, clone_db_object
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.qrws_connection import BasicConnection
from quadradiusr_server.qrws_messages import Message, KickMessage


@dataclass
class Square:
    elevation: int


@dataclass
class GameSettings:
    size_x: int
    size_y: int


@dataclass
class GameState:
    settings: GameSettings
    squares: Dict[Tuple[int, int], Square]

    @classmethod
    def initial(cls):
        return GameState(
            settings=GameSettings(
                size_x=10,
                size_y=10,
            ),
            squares={
                (x, y): Square(elevation=0)
                for x in range(10) for y in range(10)
            },
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
        await self.repository.game_repository.save(self.game)

    def serialize_game_state(self, game_state: GameState):
        return {
            'settings': self.serialize_game_settings(game_state.settings),
            'board': self.serialize_board(game_state),
        }

    def serialize_game_settings(self, settings: GameSettings):
        return {
            'size_x': settings.size_x,
            'size_y': settings.size_y,
        }

    def serialize_board(self, game_state: GameState):
        return {
            'squares': [
                self.serialize_square(pos, square)
                for pos, square in game_state.squares.values()
            ],
        }

    def serialize_square(self, pos: (int, int), square: Square):
        return {
            'x': pos[0],
            'y': pos[1],
            'elevation': square.elevation,
        }


class GameConnection(BasicConnection):
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
