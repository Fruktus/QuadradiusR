import asyncio
import copy
from dataclasses import dataclass
from typing import Dict, Optional

from quadradiusr_server.config import GameConfig
from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Game
from quadradiusr_server.db.base import User
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.game_state import GameState, Piece, Tile
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.powers import PowerDefinition, PowerRandomizer
from quadradiusr_server.qrws_connection import BasicConnection, QrwsConnection
from quadradiusr_server.qrws_messages import Message, KickMessage, GameStateMessage, MoveMessage, \
    MoveResultMessage, GameStateDiffMessage


@dataclass
class MoveResult:
    is_legal: bool
    reason: Optional[str] = None
    old_game_state: Optional[GameState] = None
    new_game_state: Optional[GameState] = None


class GameInProgress:
    def __init__(self, game: Game, repository: Repository, config: GameConfig) -> None:
        self.config = config
        self.game_id = game.id_
        self.repository = repository

        self.player_connections: Dict[str, Optional[GameConnection]] = {
            game.player_a_id_: None,
            game.player_b_id_: None,
        }

        self.power_randomizer: PowerRandomizer = config.get_power_randomizer()
        self.power_definitions: Dict[str, PowerDefinition] = config.get_power_definitions()

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
        old_game_state = copy.deepcopy(game.game_state_)

        # we need to make sure sqlalchemy will see the change
        game_state: GameState = copy.deepcopy(game.game_state_)
        game.game_state_ = game_state

        tiles = game_state.board.tiles
        pieces = game_state.board.pieces
        other_player_id = game.get_other_player_id(player.id_)

        if game_state.finished:
            return MoveResult(
                is_legal=False,
                reason='Game is finished',
            )

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
            if tiles[other_piece.tile_id].position == dest_tile.position:
                captured_pieces.append(opid)

        for captured_piece in captured_pieces:
            del pieces[captured_piece]

        piece.tile_id = tile_id
        game_state.current_player_id = other_player_id

        if not any(piece.owner_id == other_player_id for piece in pieces.values()):
            game_state.finished = True
            game_state.winner_id = player.id_
        else:
            self.power_randomizer.after_move(
                game_state, list(self.power_definitions.values()))

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
            r = await self.game_in_progress.make_move(
                user,
                piece_id=message.piece_id,
                tile_id=message.tile_id,
            )

            async def on_commit(conn: GameConnection, result: MoveResult):
                await conn.qrws.send_message(MoveResultMessage(
                    is_legal=result.is_legal,
                    reason=result.reason,
                ))
                if not result.is_legal:
                    return
                coroutines = []
                for player_id, conn in conn.game_in_progress.player_connections.items():
                    diff, etag_from, etag_to = GameState.serialize_diff_with_etag_for(
                        from_=result.old_game_state,
                        to=result.new_game_state,
                        user_id=player_id,
                    )
                    coroutines.append(conn.qrws.send_message(GameStateDiffMessage(
                        recipient_id=player_id,
                        game_state_diff=diff,
                        etag_from=etag_from,
                        etag_to=etag_to,
                    )))
                await asyncio.gather(*coroutines)

            await self.repository.synchronize_transaction_on_commit(
                on_commit(self, r))
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
