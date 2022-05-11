from unittest import IsolatedAsyncioTestCase

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.config import DatabaseConfig
from quadradiusr_server.db.access_token_repository import AccessTokenRepository
from quadradiusr_server.db.base import AccessToken
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.transactions import transaction_context
from quadradiusr_server.utils import parse_iso_datetime_tz


class TestAccessToken(IsolatedAsyncioTestCase):

    async def test_initialize(self):
        database = DatabaseEngine(DatabaseConfig(
            create_metadata=True,
        ))

        await database.initialize()
        async with transaction_context(database) as session:
            session: AsyncSession
            repo = AccessTokenRepository(database)
            created_at = parse_iso_datetime_tz('2000-01-01T00:00:00Z')
            accessed_at = parse_iso_datetime_tz('2000-01-01T10:00:00Z')
            await session.execute(insert(AccessToken), [{
                'id_': 'id',
                'user_id_': 'asdf',
                'token_': 'token',
                'created_at_': created_at,
                'accessed_at_': accessed_at,
            }])

            result = await repo.get('token', created_later_than=created_at)
            self.assertIsNone(result)

            result = await repo.get('token', accessed_later_than=accessed_at)
            self.assertIsNone(result)

            result = await repo.get('token')
            self.assertEqual('id', result.id_)
            self.assertEqual('asdf', result.user_id_)
            self.assertEqual('token', result.token_)
            self.assertEqual(created_at, result.created_at_)
            self.assertTrue(result.accessed_at_ > accessed_at)
