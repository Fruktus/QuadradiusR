import datetime
from typing import Optional

from sqlalchemy import delete
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
    async def remove(
            self, game_invite: GameInvite,
            *, db_session: AsyncSession):
        result = await db_session.execute(
            delete(GameInvite).where(GameInvite.id_ == game_invite.id_))
        # TODO

    @transactional
    async def purge_old_invites(
            self,
            *, db_session: AsyncSession):
        result = await db_session.execute(
            delete(GameInvite).where(GameInvite.expiration_ < datetime.datetime.now()))
        # TODO
