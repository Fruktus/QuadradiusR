from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness
from quadradiusr_server.db.transactions import transaction_context


class TestAuth(IsolatedAsyncioTestCase, RestTestHarness, TestUserHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_authorize(self):
        async with transaction_context(self.server.database):
            await self.server.repository.user_repository.add(self.get_test_user())
            username = self.get_test_user().username_
            password = self.get_test_user_password()

        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url('/authorize'), json={
                'username': username,
                'password': password,
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                token = body['token']

            async with session.get(self.server_url('/user/@me'), headers={
                'authorization': token,
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual(username, body['username'])
