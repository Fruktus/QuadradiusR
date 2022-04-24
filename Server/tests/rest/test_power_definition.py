from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness


class TestPowerDefinition(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_list(self):
        await self.create_test_user(0)

        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/power-definition'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertIsInstance(body, list)
                self.assertEqual(1, len(body))

    async def test_raise_tile(self):
        await self.create_test_user(0)

        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/power-definition/raise_tile'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual({
                    'id': 'raise_tile',
                    'name': 'Raise Tile',
                    'description': 'Raises the tile',
                }, body)
