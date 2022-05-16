import base64
import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List

import jsondiff as jsondiff

from quadradiusr_server.utils import SimpleJsonDiffSyntax


@dataclass
class Tile:
    id: str
    position: Tuple[int, int]
    elevation: int = 0

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
    id: str
    owner_id: str
    tile_id: str

    def serialize_for(self, user_id: str):
        return {
            'owner_id': self.owner_id,
            'tile_id': self.tile_id,
        }


@dataclass
class Power:
    id: str
    power_definition_id: str
    tile_id: Optional[str]
    piece_id: Optional[str] = None
    authorized_player_ids: List[str] = field(default_factory=list)

    def serialize_for(self, user_id: str):
        authorized = user_id in self.authorized_player_ids
        return {
            'power_definition_id': self.power_definition_id if authorized else None,
            'tile_id': self.tile_id,
            'piece_id': self.piece_id,
            'authorized_player_ids': self.authorized_player_ids,
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
    powers: Dict[str, Power] = field(default_factory=dict)

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
            'powers': {
                power_id: power.serialize_for(user_id)
                for power_id, power in self.powers.items()
            },
        }

    def get_tile_at(self, x: int, y: int) -> Optional[Tile]:
        for tile in self.tiles.values():
            if tile.position == (x, y):
                return tile

    def get_piece_on(self, tile_id: str) -> Optional[Piece]:
        for piece in self.pieces.values():
            if piece.tile_id == tile_id:
                return piece

    def get_piece_at(self, x: int, y: int) -> Optional[Piece]:
        tile = self.get_tile_at(x, y)
        if tile is None:
            return None
        return self.get_piece_on(tile.id)

    def get_empty_tiles(self) -> Dict[str, Tile]:
        # skip tiles which have pieces on them
        tiles = dict(self.tiles)
        for piece in self.pieces.values():
            del tiles[piece.tile_id]

        # skip tiles which have powers on them
        for power in self.powers.values():
            if power.tile_id:
                del tiles[power.tile_id]

        return tiles


@dataclass
class NextPowerSpawnInfo:
    rounds: int
    count: int

    def serialize_for(self, user_id: str) -> dict:
        return {
            'rounds': self.rounds,
            'count': self.count,
        }


@dataclass
class GameState:
    settings: GameSettings
    board: GameBoard
    current_player_id: str
    next_power_spawn: NextPowerSpawnInfo
    finished: bool = False
    winner_id: Optional[str] = None
    moves_played: int = 0

    def serialize_for(self, user_id: str) -> dict:
        return {
            'settings': self.settings.serialize_for(user_id),
            'board': self.board.serialize_for(user_id),
            'current_player_id': self.current_player_id,
            'next_power_spawn': self.next_power_spawn.serialize_for(user_id),
            'finished': self.finished,
            'winner_id': self.winner_id,
            'moves_played': self.moves_played,
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

        diff = jsondiff.diff(
            from_serialized, to_serialized,
            marshal=True, syntax=SimpleJsonDiffSyntax())
        return diff, from_etag, to_etag

    @classmethod
    def initial(cls, player_a_id: str, player_b_id: str):
        board_size = (10, 8)
        tiles = dict()
        for x in range(board_size[0]):
            for y in range(board_size[1]):
                tile = Tile(
                    id=str(uuid.uuid4()),
                    position=(x, y),
                )
                tiles[tile.id] = tile

        pieces = dict()
        for x in range(board_size[0]):
            for y in range(2):
                piece = Piece(
                    id=str(uuid.uuid4()),
                    owner_id=player_a_id,
                    tile_id=[
                        tile_id for tile_id, tile in tiles.items()
                        if tile.position == (x, y)
                    ][0],
                )
                pieces[piece.id] = piece
                piece = Piece(
                    id=str(uuid.uuid4()),
                    owner_id=player_b_id,
                    tile_id=[
                        tile_id for tile_id, tile in tiles.items()
                        if tile.position == (x, y + board_size[1] - 2)
                    ][0],
                )
                pieces[piece.id] = piece

        return GameState(
            settings=GameSettings(
                board_size=board_size,
            ),
            board=GameBoard(
                tiles=tiles,
                pieces=pieces,
            ),
            current_player_id=player_a_id,
            next_power_spawn=NextPowerSpawnInfo(
                rounds=0,
                count=0,
            )
        )
