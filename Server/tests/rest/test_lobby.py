from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness


class TestLobby(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_main_lobby(self):
        await self.create_test_user(0)

        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/lobby'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual([{
                    'id': '@main',
                    'name': 'Main',
                    'ws_url': 'ws://example.com/lobby/@main'
                }], body)

            async with session.get(self.server_url('/lobby/@main'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual({
                    'id': '@main',
                    'name': 'Main',
                    'ws_url': 'ws://example.com/lobby/@main'
                }, body)
