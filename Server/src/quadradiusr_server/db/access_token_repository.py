from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.db.base import User, AccessToken
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.transactions import transactional


class AccessTokenRepository:
    def __init__(self, database: DatabaseEngine) -> None:
        self.database = database

    @transactional
    async def add(
            self, user: User,
            *, db_session: AsyncSession):
        db_session.add(user)

    @transactional
    async def get(
            self, token: str, *,
            db_session: AsyncSession) -> Optional[AccessToken]:
        now = datetime.now(tz=timezone.utc)
        result = await db_session.execute(
            select(AccessToken).where(and_(
                AccessToken.token_ == token,
                or_(AccessToken.expires_at_ is None, AccessToken.expires_at_ > now),
                or_(AccessToken.access_expires_at_ is None, AccessToken.access_expires_at_ > now),
            )))
        return result.scalar_one_or_none()

    @transactional
    async def remove_old_tokens(
            self, *, db_session: AsyncSession):
        now = datetime.now(tz=timezone.utc)
        await db_session.execute(
            delete(AccessToken).where(or_(
                AccessToken.expires_at_ <= now,
                AccessToken.access_expires_at_ <= now,
                )))
