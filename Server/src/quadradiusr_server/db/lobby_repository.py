from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.db.base import Lobby, LobbyMessage
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.transactions import transactional


class LobbyRepository:
    def __init__(self, database: DatabaseEngine) -> None:
        self.database = database

    @transactional
    async def get_by_id(
            self, id_: str,
            *, db_session: AsyncSession) -> Optional[Lobby]:
        stmt = select(Lobby) \
            .where(Lobby.id_ == id_)
        result = await db_session.execute(stmt)
        return result.scalar()

    @transactional
    async def get_all(
            self, *, db_session: AsyncSession) -> List[Lobby]:
        result = await db_session.execute(select(Lobby))
        return result.scalars()

    @transactional
    async def add(
            self, lobby: Lobby,
            *, db_session: AsyncSession):
        db_session.add(lobby)

    @transactional
    async def add_message(
            self, lobby_message: LobbyMessage,
            *, db_session: AsyncSession):
        db_session.add(lobby_message)

    @transactional
    async def get_all_messages(
            self, lobby: Lobby, *, db_session: AsyncSession) -> List[Lobby]:
        result = await db_session.execute(
            select(LobbyMessage).where(LobbyMessage.lobby_id_ == lobby.id_))
        return result.scalars()
