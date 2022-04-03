from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import TestUserHarness, RestTestHarness


class TestGateway(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_gateway_info(self):
        async with aiohttp.ClientSession() as session, \
                session.get(self.server_url('/gateway')) as response:
            self.assertEqual(200, response.status)

            body = await response.json()
            self.assertEqual('ws://example.com/gateway', body['url'])
