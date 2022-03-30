from unittest import IsolatedAsyncioTestCase

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.config import DatabaseConfig
from quadradiusr_server.db.base import User
from quadradiusr_server.db.database_engine import DatabaseEngine


class TestDatabaseEngine(IsolatedAsyncioTestCase):

    async def test_initialize(self):
        database = DatabaseEngine(DatabaseConfig(
            create_metadata=True,
        ))

        await database.initialize()
        async with database.session() as session:
            session: AsyncSession
            await session.execute(insert(User), [{
                'id_': 'xyz',
                'username_': 'username',
                'password_': 'password',
            }])
            result = await session.execute(select(User))
            user = result.scalar()
            self.assertEqual('xyz', user.id_)
            self.assertEqual('username', user.username_)
            self.assertEqual('password', user.password_)
