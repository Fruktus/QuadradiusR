import re
from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness
from quadradiusr_server.db.base import User
from quadradiusr_server.db.transactions import transaction_context


class TestUser(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

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
            user = User(
                id_='696969',
                username_='cushy_moconut',
                password_='xyz',
            )

            await self.server.repository.user_repository.add(user)
            token = await self.server.auth.issue_token(user)

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

    async def test_create_user(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url('/user'), json={
                'username': 'test_user',
                'password': 'test_password',
            }) as response:
                self.assertEqual(201, response.status)
                loc = response.headers['location']
                self.assertRegex(loc, '/user/[^/]+')

            user_id = re.match('/user/(.*)', loc).group(1)

            async with transaction_context(self.server.database):
                user = await self.server.repository.user_repository.get_by_id(user_id)
                token = await self.server.auth.issue_token(user)

            async with session.get(self.server_url(loc), headers={
                'authorization': token,
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual(user_id, body['id'])
                self.assertEqual('test_user', body['username'])

    async def test_create_user_already_exists(self):
        await self.create_test_user(0)
        username = self.get_test_user_username(0)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.server_url('/user'), json={
                'username': username,
                'password': 'test_password',
            }) as response:
                self.assertEqual(409, response.status)
                self.assertEqual(
                    '409: User already exists',
                    await response.text())
