from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
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
            created_later_than: datetime = None,
            accessed_later_than: datetime = None,
            db_session: AsyncSession) -> Optional[AccessToken]:
        result = await db_session.execute(
            select(AccessToken).where(and_(
                AccessToken.token_ == token,
                AccessToken.created_at_ > created_later_than if created_later_than else True,
                AccessToken.accessed_at_ > accessed_later_than if accessed_later_than else True,
            )))
        access_token = result.one_or_none()
        if access_token:
            at: AccessToken = access_token.AccessToken
            at.accessed_at_ = datetime.now(timezone.utc)
            return at
        else:
            return None
