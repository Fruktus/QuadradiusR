import asyncio
from unittest import IsolatedAsyncioTestCase

import aiohttp
from async_timeout import timeout

from harness import TestUserHarness, RestTestHarness, WebsocketHarness
from quadradiusr_server.constants import QrwsOpcode


class E2eLobbyJoinNotificationTest(
    IsolatedAsyncioTestCase,
    WebsocketHarness,
    TestUserHarness,
    RestTestHarness,
):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_lobby_join_notification(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
            self.create_test_user(2),
        )
        lobby_ws = self.server_url('/lobby/@main/connect', protocol='ws')

        user2 = await self.get_test_user(2)

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(lobby_ws) as ws0, \
                    session.ws_connect(lobby_ws) as ws1:
                await asyncio.gather(
                    self.authorize_ws(0, ws0),
                    self.authorize_ws(1, ws1),
                )

                for ws in [ws0, ws1]:
                    await self.ws_subscribe(ws, 'lobby.*')

                async with session.ws_connect(lobby_ws) as ws2:
                    await self.authorize_ws(2, ws2)

                    expected_data = {
                        'topic': 'lobby.joined',
                        'data': {
                            'lobby_id': '@main',
                            'user': {
                                'id': user2['id'],
                                'username': user2['username']
                            },
                        },
                    }
                    data = await ws0.receive_json()
                    self.assertEqual(QrwsOpcode.NOTIFICATION, data['op'])
                    self.assertEqual(expected_data, data['d'])
                    data = await ws1.receive_json()
                    self.assertEqual(QrwsOpcode.NOTIFICATION, data['op'])
                    self.assertEqual(expected_data, data['d'])

                expected_data = {
                    'topic': 'lobby.left',
                    'data': {
                        'lobby_id': '@main',
                        'user_id': user2['id'],
                    },
                }
                data = await ws0.receive_json()
                self.assertEqual(QrwsOpcode.NOTIFICATION, data['op'])
                self.assertEqual(expected_data, data['d'])
                data = await ws1.receive_json()
                self.assertEqual(QrwsOpcode.NOTIFICATION, data['op'])
                self.assertEqual(expected_data, data['d'])

    async def test_duplicate_notifications(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )
        lobby_ws = self.server_url('/lobby/@main/connect', protocol='ws')

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(lobby_ws) as ws0:
                await asyncio.gather(
                    self.authorize_ws(0, ws0),
                )

                await self.ws_subscribe(ws0, '*')
                await self.ws_subscribe(ws0, '*')
                await self.ws_subscribe(ws0, 'lobby.*')

                async with session.ws_connect(lobby_ws) as ws1:
                    await self.authorize_ws(1, ws1)

                    data = await ws0.receive_json()
                    self.assertEqual(QrwsOpcode.NOTIFICATION, data['op'])
                    try:
                        msg = await ws0.receive_json(timeout=0.00001)
                        raise AssertionError(f'Received unexpected message: {msg}')
                    except asyncio.TimeoutError:
                        pass
