import asyncio
import datetime
from unittest import IsolatedAsyncioTestCase

import aiohttp
from async_timeout import timeout

from harness import TestUserHarness, RestTestHarness
from quadradiusr_server.constants import QrwsOpcode


class E2eGameInviteNotificationTest(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_notification_about_game_invite(self):
        # user0 sends invite to user1,
        # user1 should receive notification, but not user0 and user2
        await self.create_test_user(0)
        await self.create_test_user(1)
        await self.create_test_user(2)
        gateway_ws = self.server_url('/gateway', protocol='ws')

        user1 = await self.get_test_user(1)

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(gateway_ws) as ws0, \
                    session.ws_connect(gateway_ws) as ws1, \
                    session.ws_connect(gateway_ws) as ws2:
                await ws0.send_json({
                    'op': QrwsOpcode.IDENTIFY,
                    'd': {
                        'token': await self.authorize_test_user(0),
                    },
                })
                data = await ws0.receive_json()
                self.assertEqual(QrwsOpcode.SERVER_READY, data['op'])
                await ws1.send_json({
                    'op': QrwsOpcode.IDENTIFY,
                    'd': {
                        'token': await self.authorize_test_user(1),
                    },
                })
                data = await ws1.receive_json()
                self.assertEqual(QrwsOpcode.SERVER_READY, data['op'])
                await ws2.send_json({
                    'op': QrwsOpcode.IDENTIFY,
                    'd': {
                        'token': await self.authorize_test_user(2),
                    },
                })
                data = await ws2.receive_json()
                self.assertEqual(QrwsOpcode.SERVER_READY, data['op'])

                await ws1.send_json({
                    'op': QrwsOpcode.SUBSCRIBE,
                    'd': {
                        'topic': 'game.invite.received',
                    },
                })
                data = await ws1.receive_json()
                self.assertEqual(QrwsOpcode.SUBSCRIBED, data['op'])

                exp = datetime.datetime.now() + datetime.timedelta(seconds=60)
                async with session.post(self.server_url('/game_invite'), json={
                    'subject': user1['id'],
                    'expiration': exp.isoformat(),
                }, headers={
                    'authorization': await self.authorize_test_user(0)
                }) as response:
                    self.assertEqual(201, response.status)

                with self.assertRaises(asyncio.exceptions.TimeoutError):
                    await ws0.receive_json(timeout=0.01)
                with self.assertRaises(asyncio.exceptions.TimeoutError):
                    await ws2.receive_json(timeout=0.01)

                data = await ws1.receive_json(timeout=0.01)
                self.assertEqual(QrwsOpcode.NOTIFICATION, data['op'])
