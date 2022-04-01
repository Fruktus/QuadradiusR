from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.game_invite_repository import GameInviteRepository
from quadradiusr_server.db.game_repository import GameRepository
from quadradiusr_server.db.user_repository import UserRepository


class Repository:
    def __init__(self, database: DatabaseEngine) -> None:
        self._database = database
        self._user_repository = UserRepository(database)
        self._game_invite_repository = GameInviteRepository(database)
        self._game_repository = GameRepository(database)

    @property
    def database(self) -> DatabaseEngine:
        return self._database

    @property
    def user_repository(self) -> UserRepository:
        return self._user_repository

    @property
    def game_invite_repository(self) -> GameInviteRepository:
        return self._game_invite_repository

    @property
    def game_repository(self) -> GameRepository:
        return self._game_repository
