import datetime
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.db.base import GameInvite
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.transactions import transactional


class GameInviteRepository:
    def __init__(self, database: DatabaseEngine) -> None:
        self.database = database

    @transactional
    async def get_by_id(
            self, id_: str,
            *, db_session: AsyncSession) -> Optional[GameInvite]:
        return await db_session.get(GameInvite, id_)

    @transactional
    async def add(
            self, game_invite: GameInvite,
            *, db_session: AsyncSession):
        db_session.add(game_invite)

    @transactional
    async def get_old_invites(
            self, *, db_session: AsyncSession) -> List[GameInvite]:
        now = datetime.datetime.now(datetime.timezone.utc)
        result = await db_session.execute(
            select(GameInvite).where(GameInvite.expires_at_ < now))
        return result.scalars()

    @transactional
    async def remove(
            self, game_invite: GameInvite,
            *, db_session: AsyncSession):
        await db_session.delete(game_invite)
