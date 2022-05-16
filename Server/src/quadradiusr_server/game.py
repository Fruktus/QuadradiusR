import asyncio
import copy
import logging
from dataclasses import dataclass
from typing import Dict, Optional

from quadradiusr_server.config import GameConfig
from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Game
from quadradiusr_server.db.base import User
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.game_state import GameState, Piece, Tile, GameBoard
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.powers import PowerDefinition, PowerRandomizer
from quadradiusr_server.qrws_connection import BasicConnection, QrwsConnection
from quadradiusr_server.qrws_messages import Message, KickMessage, GameStateMessage, MoveMessage, \
    ActionResultMessage, GameStateDiffMessage, ApplyPowerMessage


@dataclass
class ActionResult:
    is_legal: bool
    reason: Optional[str] = None
    old_game_state: Optional[GameState] = None
    new_game_state: Optional[GameState] = None


class ActionApplicationContext:
    def __init__(self, game: Game) -> None:
        self._game = game
        self._old_game_state = copy.deepcopy(self._game.game_state_)

        # we need to make sure sqlalchemy will see the change
        game_state: GameState = copy.deepcopy(self._game.game_state_)
        self._game.game_state_ = game_state
        self._new_game_state = game_state

    @property
    def old_game_state(self):
        return self._old_game_state

    @property
    def new_game_state(self):
        return self._new_game_state

    @property
    def game_state(self):
        return self.new_game_state

    def legal_result(self):
        return ActionResult(
            is_legal=True,
            old_game_state=self.old_game_state,
            new_game_state=self.game_state,
        )


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

        logging.info(f'User {connection.user_id} connected to game {self.game_id}')

    async def disconnect_player(self, connection: 'GameConnection'):
        player_id = connection.user_id
        if player_id in self.player_connections:
            self.player_connections[player_id] = None

        logging.info(f'User {connection.user_id} disconnected from game {self.game_id}')

    async def apply_power(
            self, player: User,
            power_id: str) -> ActionResult:
        ctx = ActionApplicationContext(await self.get_game())
        game_state: GameState = ctx.game_state

        if game_state.finished:
            return ActionResult(
                is_legal=False,
                reason='Game is finished',
            )

        if game_state.current_player_id != player.id_:
            return ActionResult(
                is_legal=False,
                reason='Not your turn',
            )

        if power_id not in game_state.board.powers:
            return ActionResult(
                is_legal=False,
                reason='Power does not exist',
            )

        power = game_state.board.powers[power_id]

        if power.tile_id is not None:
            return ActionResult(
                is_legal=False,
                reason='Power has not been captured',
            )

        if player.id_ not in power.authorized_player_ids:
            return ActionResult(
                is_legal=False,
                reason='You do not own the power',
            )

        pd_id = power.power_definition_id
        pd = self.power_definitions[pd_id]

        pd.apply(game_state, power_id)

        return ctx.legal_result()

    async def make_move(
            self, player: User,
            piece_id: str,
            tile_id: str) -> ActionResult:
        game = await self.get_game()
        ctx = ActionApplicationContext(game)
        # check move

        game_state: GameState = ctx.game_state

        tiles = game_state.board.tiles
        pieces = game_state.board.pieces
        other_player_id = game.get_other_player_id(player.id_)

        if game_state.finished:
            return ActionResult(
                is_legal=False,
                reason='Game is finished',
            )

        if game_state.current_player_id != player.id_:
            return ActionResult(
                is_legal=False,
                reason='Not your turn',
            )

        if piece_id not in pieces:
            return ActionResult(
                is_legal=False,
                reason='Piece does not exist',
            )
        if tile_id not in tiles:
            return ActionResult(
                is_legal=False,
                reason='Destination tile does not exist',
            )

        piece: Piece = pieces[piece_id]

        if piece.owner_id != player.id_:
            return ActionResult(
                is_legal=False,
                reason='Cannot move opponent\'s piece',
            )

        src_tile: Tile = tiles[piece.tile_id]
        dest_tile: Tile = tiles[tile_id]

        if dest_tile.elevation > src_tile.elevation + 1:
            return ActionResult(
                is_legal=False,
                reason='Destination tile too high',
            )

        # perform move
        game_state.moves_played += 1

        await self._capture_pieces(dest_tile, game_state.board)
        await self._capture_powers(dest_tile, piece, game_state.board)

        piece.tile_id = tile_id
        game_state.current_player_id = other_player_id

        if not any(piece.owner_id == other_player_id for piece in pieces.values()):
            game_state.finished = True
            game_state.winner_id = player.id_
        else:
            self._handle_power_spawning(game_state)

        return ctx.legal_result()

    async def _capture_pieces(
            self, dest_tile: Tile,
            board: GameBoard):
        captured_pieces = []
        for opid, other_piece in board.pieces.items():
            if board.tiles[other_piece.tile_id].position == dest_tile.position:
                captured_pieces.append(opid)
        for captured_piece in captured_pieces:
            del board.pieces[captured_piece]

    async def _capture_powers(
            self, dest_tile: Tile,
            piece: Piece,
            board: GameBoard):
        for power_id, power in board.powers.items():
            if power.tile_id is None:
                continue
            if board.tiles[power.tile_id].position == dest_tile.position:
                power.tile_id = None
                power.piece_id = piece.id
                power.authorized_player_ids.append(piece.owner_id)

    def _handle_power_spawning(self, game_state: GameState):
        self.power_randomizer.after_move(
            game_state, list(self.power_definitions.values()))


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

            if result.is_legal:
                logging.debug(
                    f'User {user.friendly_name} in game {self.game_in_progress.game_id} '
                    f'made a move {message.piece_id}->{message.tile_id}')
            else:
                logging.debug(
                    f'User {user.friendly_name} in game {self.game_in_progress.game_id} '
                    f'has tried to make an illegal move {message.piece_id}->{message.tile_id}, '
                    f'reason: {result.reason}')

            await self._post_action(result)
            return True
        elif isinstance(message, ApplyPowerMessage):
            result = await self.game_in_progress.apply_power(
                user,
                power_id=message.power_id,
            )

            if result.is_legal:
                logging.debug(
                    f'User {user.friendly_name} in game {self.game_in_progress.game_id} '
                    f'applied power {message.power_id}')
            else:
                logging.debug(
                    f'User {user.friendly_name} in game {self.game_in_progress.game_id} '
                    f'has illegally tried to apply a power {message.power_id}, '
                    f'reason: {result.reason}')

            await self._post_action(result)
            return True
        else:
            return False

    async def _post_action(self, action_result: ActionResult):
        async def on_commit(conn: GameConnection, result: ActionResult):
            await conn.qrws.send_message(ActionResultMessage(
                is_legal=result.is_legal,
                reason=result.reason,
            ))
            if not result.is_legal:
                return
            coroutines = []
            for player_id, conn in conn.game_in_progress.player_connections.items():
                if conn is None:
                    continue
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
            on_commit(self, action_result))

    async def kick(self):
        await self.qrws.send_message(KickMessage(
            reason='Connected from another location',
        ))
        await self.qrws.close(
            QrwsCloseCode.CONFLICT,
            'Connected from another location')
