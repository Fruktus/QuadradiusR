import urllib.parse
from unittest import IsolatedAsyncioTestCase

import aiohttp
from isodate import parse_datetime

from harness import RestTestHarness, TestUserHarness
from quadradiusr_server.db.base import LobbyMessage
from quadradiusr_server.db.transactions import transaction_context


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
                    'ws_url': 'ws://example.com/lobby/@main/connect',
                    'players': None,
                }], body)

            async with session.get(self.server_url('/lobby/@main'), headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual({
                    'id': '@main',
                    'name': 'Main',
                    'ws_url': 'ws://example.com/lobby/@main/connect',
                    'players': [],
                }, body)

    async def test_message_filtering(self):
        await self.create_test_user(0)
        user0 = await self.get_test_user(0)

        dates = [
            parse_datetime('2022-01-01T10:00:20Z'),
            parse_datetime('2022-01-01T10:00:15Z'),
            parse_datetime('2022-01-01T10:00:10Z'),
            parse_datetime('2022-01-01T10:00:05Z'),
            parse_datetime('2022-01-01T10:00:00Z'),
        ]

        async with transaction_context(self.server.database):
            messages = [LobbyMessage(
                id_=f'{n}',
                user_id_=user0['id'],
                lobby_id_='@main',
                content_=f'message {n}',
                created_at_=dates[n],
            ) for n in range(5)]
            for msg in messages:
                await self.server.repository.lobby_repository.add_message(msg)

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.server_url(
                    '/lobby/@main/connect', protocol='ws')) as ws:
                await self.authorize_ws(0, ws)

                async with session.get(self.server_url('/lobby/@main/message'), headers={
                    'authorization': await self.authorize_test_user(0)
                }) as response:
                    self.assertEqual(200, response.status)
                    body = await response.json()
                    self.assertEqual(5, len(body))

                async with session.get(self.server_url('/lobby/@main/message?limit=3'), headers={
                    'authorization': await self.authorize_test_user(0)
                }) as response:
                    self.assertEqual(200, response.status)
                    body = await response.json()
                    self.assertEqual(3, len(body))
                    self.assertEqual('0', body[0]['id'])
                    self.assertEqual('1', body[1]['id'])
                    self.assertEqual('2', body[2]['id'])

                before = urllib.parse.quote(dates[2].isoformat())
                async with session.get(self.server_url(f'/lobby/@main/message?before={before}'), headers={
                    'authorization': await self.authorize_test_user(0)
                }) as response:
                    self.assertEqual(200, response.status)
                    body = await response.json()
                    self.assertEqual(2, len(body))
                    self.assertEqual('3', body[0]['id'])
                    self.assertEqual('4', body[1]['id'])

                before = urllib.parse.quote('2022-01-01T11:00:10+01:00')
                async with session.get(self.server_url(f'/lobby/@main/message?before={before}'), headers={
                    'authorization': await self.authorize_test_user(0)
                }) as response:
                    self.assertEqual(200, response.status)
                    body = await response.json()
                    self.assertEqual(2, len(body))

                before = urllib.parse.quote('2022-01-01T10:00:10')
                async with session.get(self.server_url(f'/lobby/@main/message?before={before}'), headers={
                    'authorization': await self.authorize_test_user(0)
                }) as response:
                    self.assertEqual(400, response.status)
                    body = await response.text()
                    self.assertEqual('400: Malformed query params', body)
