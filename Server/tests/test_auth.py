from unittest import IsolatedAsyncioTestCase

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from quadradiusr_server.auth import hash_password, check_password, Auth
from quadradiusr_server.config import DatabaseConfig, AuthConfig
from quadradiusr_server.db.base import User
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transaction_context


class AuthTest(IsolatedAsyncioTestCase):
    async def test_hashing(self):
        h = hash_password(b'asdf')

        self.assertTrue(check_password(b'asdf', h))
        self.assertFalse(check_password(b'asdf2', h))

    async def test_login(self):
        database = DatabaseEngine(DatabaseConfig(
            create_metadata=True,
        ))
        auth = Auth(AuthConfig(), Repository(database))

        await database.initialize()
        async with transaction_context(database) as session:
            conn: AsyncConnection
            await session.execute(insert(User), [{
                'id_': '696969',
                'username_': 'cushy_moconut',
                'password_': hash_password(b'okon'),
            }])

            user = await auth.login('cushy_moconut', b'okon')
            self.assertIsNotNone(user)
            self.assertEqual('696969', user.id_)
