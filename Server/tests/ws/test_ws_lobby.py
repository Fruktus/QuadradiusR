import asyncio
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
                    '/lobby/@main/connect', protocol='ws')) as ws:
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

        user0 = await self.get_test_user(0)

        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws0, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws1, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws2:
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
                self.assertEqual(user0['id'], data['d']['user_id'])
                self.assertEqual('test message', data['d']['content'])

            async with session.get(self.server_url('/lobby/@main/message'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual(1, len(body))
                self.assertEqual({
                    'id': user0['id'],
                    'username': user0['username']
                }, body[0]['user'])
                self.assertEqual('test message', body[0]['content'])

    async def test_persist_messages(self):
        await self.create_test_user(0)
        await self.create_test_user(1)

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws0, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws1:
            await self.authorize_ws(0, ws0)
            await self.authorize_ws(1, ws1)

            await ws0.send_json({
                'op': QrwsOpcode.SEND_MESSAGE,
                'd': {
                    'content': 'test message 1',
                },
            })

            await ws1.send_json({
                'op': QrwsOpcode.SEND_MESSAGE,
                'd': {
                    'content': 'test message 2',
                },
            })

            await ws0.send_json({
                'op': QrwsOpcode.SEND_MESSAGE,
                'd': {
                    'content': 'test message 3',
                },
            })

            async with session.get(self.server_url('/lobby/@main/message'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual(3, len(body))
                self.assertEqual({
                    'id': user0['id'],
                    'username': user0['username']
                }, body[0]['user'])
                self.assertEqual('test message 3', body[0]['content'])
                self.assertEqual({
                    'id': user1['id'],
                    'username': user1['username']
                }, body[1]['user'])
                self.assertEqual('test message 2', body[1]['content'])
                self.assertEqual({
                    'id': user0['id'],
                    'username': user0['username']
                }, body[2]['user'])
                self.assertEqual('test message 1', body[2]['content'])

    async def test_lobby_players(self):
        await self.create_test_user(0)
        await self.create_test_user(1)
        await self.create_test_user(2)

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)
        user2 = await self.get_test_user(2)

        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws0, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws1, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws2:
            await self.authorize_ws(0, ws0)
            await self.authorize_ws(1, ws1)
            await self.authorize_ws(2, ws2)

            async with session.get(self.server_url('/lobby/@main'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertSetEqual({
                    user0['id'],
                    user1['id'],
                    user2['id'],
                }, {p['id'] for p in body['players']})

    async def test_lobby_connect_duplicate_user(self):
        await self.create_test_user(0)

        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws0, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws1:
            await self.authorize_ws(0, ws0)
            await ws1.send_json({
                'op': QrwsOpcode.IDENTIFY,
                'd': {
                    'token': await self.authorize_test_user(0),
                },
            })
            data = await ws1.receive_json()
            self.assertEqual(QrwsOpcode.ERROR, data['op'])
            self.assertEqual('You are already connected to this lobby', data['d']['message'])
            self.assertEqual(True, data['d']['fatal'])

    async def test_lobby_connect_duplicate_user_force(self):
        await self.create_test_user(0)

        async with timeout(2000), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws0, \
                session.ws_connect(self.server_url(
                    '/lobby/@main/connect?force=true', protocol='ws')) as ws1:
            await self.authorize_ws(0, ws0)
            await self.authorize_ws(0, ws1)

            data = await ws0.receive_json()
            self.assertEqual(QrwsOpcode.KICK, data['op'])
