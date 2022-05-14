import datetime
from unittest import IsolatedAsyncioTestCase

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.config import DatabaseConfig
from quadradiusr_server.db.access_token_repository import AccessTokenRepository
from quadradiusr_server.db.base import AccessToken
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.transactions import transaction_context


class TestAccessToken(IsolatedAsyncioTestCase):

    async def test_initialize(self):
        database = DatabaseEngine(DatabaseConfig(
            create_metadata=True,
            hide_parameters=False,
        ))

        await database.initialize()
        async with transaction_context(database) as session:
            session: AsyncSession
            repo = AccessTokenRepository(database)

            now = datetime.datetime.now(tz=datetime.timezone.utc)
            past = now - datetime.timedelta(seconds=100)
            future = now + datetime.timedelta(seconds=100)

            await session.execute(insert(AccessToken), [{
                'id_': 'id1',
                'user_id_': 'asdf',
                'token_': 'valid_token',
                'created_at_': past,
                'accessed_at_': past,
                'expires_at_': future,
                'access_expires_at_': future,
            }])
            await session.execute(insert(AccessToken), [{
                'id_': 'id2',
                'user_id_': 'asdf',
                'token_': 'token_expired_1',
                'created_at_': past,
                'accessed_at_': past,
                'expires_at_': now,
                'access_expires_at_': future,
            }])
            await session.execute(insert(AccessToken), [{
                'id_': 'id3',
                'user_id_': 'asdf',
                'token_': 'token_expired_2',
                'created_at_': past,
                'accessed_at_': past,
                'expires_at_': future,
                'access_expires_at_': now,
            }])

            result = await repo.get('token_expired_1')
            self.assertIsNone(result)

            result = await repo.get('token_expired_2')
            self.assertIsNone(result)

            result = await repo.get('valid_token')
            self.assertEqual('id1', result.id_)
            self.assertEqual('asdf', result.user_id_)
            self.assertEqual('valid_token', result.token_)
            self.assertEqual(past, result.created_at_)
            self.assertEqual(past, result.accessed_at_)
