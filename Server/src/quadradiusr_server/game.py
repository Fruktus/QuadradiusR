import asyncio
import base64
import copy
import json
import uuid
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import jsondiff as jsondiff

from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Game
from quadradiusr_server.db.base import User
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import BasicConnection, QrwsConnection
from quadradiusr_server.qrws_messages import Message, KickMessage, GameStateMessage, MoveMessage, \
    MoveResultMessage, GameStateDiffMessage


@dataclass
class Tile:
    position: Tuple[int, int]
    elevation: int

    def serialize_for(self, user_id: str):
        return {
            'position': {
                'x': self.position[0],
                'y': self.position[1],
            },
            'elevation': self.elevation,
        }


@dataclass
class Piece:
    owner_id: str
    tile_id: str

    def serialize_for(self, user_id: str):
        return {
            'owner_id': self.owner_id,
            'tile_id': self.tile_id,
        }


@dataclass
class GameSettings:
    board_size: Tuple[int, int]

    def serialize_for(self, user_id: str):
        return {
            'board_size': {
                'x': self.board_size[0],
                'y': self.board_size[1],
            },
        }


@dataclass
class GameBoard:
    tiles: Dict[str, Tile]
    pieces: Dict[str, Piece]

    def serialize_for(self, user_id: str):
        return {
            'tiles': {
                tile_id: tile.serialize_for(user_id)
                for tile_id, tile in self.tiles.items()
            },
            'pieces': {
                piece_id: piece.serialize_for(user_id)
                for piece_id, piece in self.pieces.items()
            },
        }


@dataclass
class GameState:
    settings: GameSettings
    board: GameBoard
    current_player_id: str

    def serialize_for(self, user_id: str) -> dict:
        return {
            'settings': self.settings.serialize_for(user_id),
            'board': self.board.serialize_for(user_id),
            'current_player_id': self.current_player_id,
        }

    def serialize_with_etag_for(self, user_id: str) -> Tuple[dict, str]:
        serialized = self.serialize_for(user_id)
        hash_int = hash(json.dumps(serialized, sort_keys=True))
        hash_bytes = hash_int.to_bytes(
            hash_int.bit_length() // 8 + 1,
            byteorder='big', signed=True)
        hash_str = base64.b85encode(hash_bytes).decode()
        return serialized, hash_str

    @staticmethod
    def serialize_diff_with_etag_for(
            from_: 'GameState',
            to: 'GameState',
            user_id: str) -> Tuple[dict, str, str]:
        from_serialized, from_etag = from_.serialize_with_etag_for(user_id)
        to_serialized, to_etag = to.serialize_with_etag_for(user_id)

        diff = jsondiff.diff(from_serialized, to_serialized, marshal=True)
        return diff, from_etag, to_etag

    @classmethod
    def initial(cls, player_a_id: str, player_b_id: str):
        board_size = (10, 8)
        tiles = {
            str(uuid.uuid4()): Tile(
                position=(x, y),
                elevation=0,
            )
            for x in range(board_size[0])
            for y in range(board_size[1])
        }
        pieces = {
            str(uuid.uuid4()): Piece(
                owner_id=player_a_id,
                tile_id=[
                    tile_id for tile_id, tile in tiles.items()
                    if tile.position == (0, 0)
                ][0],
            ),
            str(uuid.uuid4()): Piece(
                owner_id=player_b_id,
                tile_id=[
                    tile_id for tile_id, tile in tiles.items()
                    if tile.position == (1, 1)
                ][0],
            ),
        }
        return GameState(
            settings=GameSettings(
                board_size=board_size,
            ),
            board=GameBoard(
                tiles=tiles,
                pieces=pieces,
            ),
            current_player_id=player_a_id,
        )


@dataclass
class MoveResult:
    is_legal: bool
    reason: Optional[str] = None
    old_game_state: Optional[GameState] = None
    new_game_state: Optional[GameState] = None


class GameInProgress:
    def __init__(self, game: Game, repository: Repository) -> None:
        self.game_id = game.id_
        self.repository = repository

        self.player_connections: Dict[str, Optional[GameConnection]] = {
            game.player_a_id_: None,
            game.player_b_id_: None,
        }

    async def get_game(self) -> Game:
        return await self.repository.game_repository.get_by_id(self.game_id)

    def is_player_connected(self, player_id):
        return self.player_connections.get(player_id) is not None

    async def connect_player(self, connection: 'GameConnection'):
        player_id = connection.user_id
        if player_id not in self.player_connections:
            raise ValueError(
                f'User {player_id} is not part of the game {self.game_id}')

        old_connection = self.player_connections.get(player_id)
        if old_connection:
            await old_connection.kick()

        self.player_connections[player_id] = connection

    async def disconnect_player(self, connection: 'GameConnection'):
        player_id = connection.user_id
        if player_id in self.player_connections:
            self.player_connections[player_id] = None

    async def make_move(
            self, player: User,
            piece_id: str,
            tile_id: str) -> MoveResult:
        # check move

        game: Game = await self.get_game()
        game_state: GameState = game.game_state_
        old_game_state = copy.deepcopy(game_state)
        tiles = game_state.board.tiles
        pieces = game_state.board.pieces

        if game_state.current_player_id != player.id_:
            return MoveResult(
                is_legal=False,
                reason='Not your turn',
            )

        if piece_id not in pieces:
            return MoveResult(
                is_legal=False,
                reason='Piece does not exist',
            )
        if tile_id not in tiles:
            return MoveResult(
                is_legal=False,
                reason='Destination tile does not exist',
            )

        piece: Piece = pieces[piece_id]

        if piece.owner_id != player.id_:
            return MoveResult(
                is_legal=False,
                reason='Cannot move opponent\'s piece',
            )

        src_tile: Tile = tiles[piece.tile_id]
        dest_tile: Tile = tiles[tile_id]

        if dest_tile.elevation > src_tile.elevation + 1:
            return MoveResult(
                is_legal=False,
                reason='Destination tile too high',
            )

        # perform move

        captured_pieces = []
        for opid, other_piece in pieces.items():
            if tiles[other_piece.tile_id].position == src_tile.position:
                captured_pieces.append(opid)

        for captured_piece in captured_pieces:
            del pieces[captured_piece]

        piece.tile_id = tile_id
        game_state.current_player_id = game.get_other_player_id(player.id_)

        return MoveResult(
            is_legal=True,
            old_game_state=old_game_state,
            new_game_state=game_state,
        )


class GameConnection(BasicConnection):

    def __init__(
            self, qrws: QrwsConnection,
            game_in_progress: GameInProgress,
            user: User,
            notification_service: NotificationService,
            repository: Repository) -> None:
        super().__init__(qrws, user, notification_service, repository)
        self.game_in_progress = game_in_progress

    async def on_ready(self, user: User):
        game = await self.game_in_progress.get_game()
        game_state = game.game_state_
        serialized, etag = game_state.serialize_with_etag_for(user)
        await self.qrws.send_message(
            GameStateMessage(
                recipient_id=user.id_,
                game_state=serialized,
                etag=etag,
            ))

    async def handle_message(self, user: User, message: Message) -> bool:
        if await super().handle_message(user, message):
            return True

        if isinstance(message, MoveMessage):
            result = await self.game_in_progress.make_move(
                user,
                piece_id=message.piece_id,
                tile_id=message.tile_id,
            )
            await self.qrws.send_message(MoveResultMessage(
                is_legal=result.is_legal,
                reason=result.reason,
            ))
            if not result.is_legal:
                return True
            coroutines = []
            for player_id, conn in self.game_in_progress.player_connections.items():
                diff, etag_from, etag_to = GameState.serialize_diff_with_etag_for(
                    from_=result.old_game_state,
                    to=result.new_game_state,
                    user_id=player_id,
                )
                coroutines.append(self.qrws.send_message(GameStateDiffMessage(
                    recipient_id=player_id,
                    game_state_diff=diff,
                    etag_from=etag_from,
                    etag_to=etag_to,
                )))
            await asyncio.gather(*coroutines)
            return True
        else:
            return False

    async def kick(self):
        await self.qrws.send_message(KickMessage(
            reason='Connected from another location',
        ))
        await self.qrws.close(
            QrwsCloseCode.CONFLICT,
            'Connected from another location')
