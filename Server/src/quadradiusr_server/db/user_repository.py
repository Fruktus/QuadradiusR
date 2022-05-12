from typing import Optional, List

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
        user = result.one_or_none()
        return user.User if user else None

    @transactional
    async def get_by_id(
            self, id_: str,
            *, db_session: AsyncSession) -> Optional[User]:
        return await db_session.get(User, id_)

    @transactional
    async def get_by_ids(
            self, ids: List[str],
            *, db_session: AsyncSession) -> List[User]:
        result = await db_session.execute(
            select(User).where(User.id_.in_(ids)))
        users = result.all()
        return [user.User for user in users]
