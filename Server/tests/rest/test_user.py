from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness
from quadradiusr_server.db.transactions import transaction_context


class TestHealth(IsolatedAsyncioTestCase, RestTestHarness, TestUserHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_user_unauthorized(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/user/@me')) as response:
                self.assertEqual(401, response.status)

    async def test_user_authorized(self):
        async with transaction_context(self.server.database):
            user = self.get_test_user()

            await self.server.repository.user_repository.add(user)
            token = self.server.auth.issue_token(user)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.server_url('/user/@me'),
                    headers={
                        'authorization': token,
                    },
            ) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual('696969', body['id'])
                self.assertEqual('cushy_moconut', body['username'])
