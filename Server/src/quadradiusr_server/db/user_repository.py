from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.db.base import User
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.transactions import transactional


class UserRepository:
    def __init__(self, database: DatabaseEngine) -> None:
        self.database = database

    @transactional
    async def add(
            self, user: User,
            *, db_session: AsyncSession):
        db_session.add(user)

    @transactional
    async def get_by_username(
            self, username: str,
            *, db_session: AsyncSession) -> Optional[User]:
        result = await db_session.execute(
            select(User).where(User.username_ == username))
        if not result:
            return None
        user = result.one()
        return user.User

    @transactional
    async def get_by_id(
            self, id_: str,
            *, db_session: AsyncSession) -> Optional[User]:
        return await db_session.get(User, id_)
