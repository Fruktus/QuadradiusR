from unittest import IsolatedAsyncioTestCase

import aiohttp
from async_timeout import timeout

from harness import RestTestHarness, TestUserHarness
from quadradiusr_server.constants import QrwsOpcode


class TestWsLobby(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_join(self):
        await self.create_test_user(0)

        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/lobby/@main', protocol='ws')) as ws:
            await ws.send_json({
                'op': QrwsOpcode.IDENTIFY,
                'd': {
                    'token': await self.authorize_test_user(0),
                },
            })
            data = await ws.receive_json()
            self.assertEqual(QrwsOpcode.SERVER_READY, data['op'])

    async def test_send_message(self):
        await self.create_test_user(0)
        await self.create_test_user(1)
        await self.create_test_user(2)

        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/lobby/@main', protocol='ws')) as ws0, \
                session.ws_connect(self.server_url(
                    '/lobby/@main', protocol='ws')) as ws1, \
                session.ws_connect(self.server_url(
                    '/lobby/@main', protocol='ws')) as ws2:
            await self.authorize_ws(0, ws0)
            await self.authorize_ws(1, ws1)
            await self.authorize_ws(2, ws2)

            await ws0.send_json({
                'op': QrwsOpcode.SEND_MESSAGE,
                'd': {
                    'content': 'test message',
                },
            })
            for ws in [ws0, ws1, ws2]:
                data = await ws.receive_json()
                self.assertEqual(QrwsOpcode.MESSAGE_SENT, data['op'])
                self.assertEqual('test message', data['d']['content'])
