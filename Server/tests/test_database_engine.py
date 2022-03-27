from unittest import IsolatedAsyncioTestCase

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncConnection

from quadradiusr_server.config import DatabaseConfig
from quadradiusr_server.db.base import DbUser
from quadradiusr_server.db.database_engine import DatabaseEngine


class TestDatabaseEngine(IsolatedAsyncioTestCase):

    async def test_initialize(self):
        engine = DatabaseEngine(DatabaseConfig(
            create_metadata=True,
        ))

        await engine.initialize()
        async with engine.connect() as conn:
            conn: AsyncConnection
            await conn.execute(insert(DbUser), [
                {
                    'id_': 'xyz'
                }
            ])
            result = await conn.execute(select(DbUser))
            self.assertEqual([('xyz', None, None)], result.fetchall())
