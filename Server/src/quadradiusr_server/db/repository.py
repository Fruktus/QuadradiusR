from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.user_repository import UserRepository


class Repository:
    def __init__(self, database: DatabaseEngine) -> None:
        self._user_repository = UserRepository(database)

    @property
    def user_repository(self) -> UserRepository:
        return self._user_repository
