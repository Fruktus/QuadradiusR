from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness


class TestHealth(IsolatedAsyncioTestCase, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_health(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/health')) as response:
                self.assertEqual(response.status, 200)

                body = await response.json()
                self.assertEqual(body['status'], 'up')
