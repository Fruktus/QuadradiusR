from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness


class TestAuth(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_authorize(self):
        await self.create_test_user(0)
        username = self.get_test_user_username(0)
        password = self.get_test_user_password(0)

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
