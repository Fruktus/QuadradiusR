from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.db.base import Game
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.transactions import transactional


class GameRepository:
    def __init__(self, database: DatabaseEngine) -> None:
        self.database = database

    @transactional
    async def get_by_id(
            self, id_: str,
            *, db_session: AsyncSession) -> Optional[Game]:
        return await db_session.get(Game, id_)

    @transactional
    async def add(
            self, game: Game,
            *, db_session: AsyncSession):
        db_session.add(game)
