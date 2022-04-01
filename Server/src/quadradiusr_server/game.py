from quadradiusr_server.db.base import Game
from quadradiusr_server.qrws_connection import BasicConnection
from quadradiusr_server.qrws_messages import Message


class GameConnection(BasicConnection):
    async def handle_message(self, message: Message) -> bool:
        if await super().handle_message(message):
            return True

        return False


class GameInProgress:
    def __init__(self, game: Game) -> None:
        self.game = game

        self.player_a_connection = None
        self.player_b_connection = None

    def is_player_connected(self, player_id):
        if self.game.player_a_id_ == player_id:
            return self.player_a_connection is not None
        if self.game.player_b_id_ == player_id:
            return self.player_b_connection is not None
        return False

    def connect_player(self, connection: GameConnection):
        if self.game.player_a_id_ == connection.user.id_:
            self.player_a_connection = connection
        if self.game.player_b_id_ == connection.user.id_:
            self.player_b_connection = connection
        raise ValueError(
            f'User {connection.user} is not part of the game {self.game}')

    def disconnect_player(self, connection: GameConnection):
        if self.player_a_connection == connection:
            self.player_a_connection = None
        if self.player_b_connection == connection:
            self.player_b_connection = None
