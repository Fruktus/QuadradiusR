import asyncio
from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness, GameHarness


class TestGame(IsolatedAsyncioTestCase, TestUserHarness, GameHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_get_game(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
            self.create_test_user(2),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])

        async with aiohttp.ClientSession() as session:
            for user_no in [0, 1]:
                async with session.get(self.server_url(f'/game/{game_id}'), headers={
                    'authorization': await self.authorize_test_user(user_no)
                }) as response:
                    self.assertEqual(200, response.status)
                    body = await response.json()
                    self.assertEqual(game_id, body['id'])
                    self.assertEqual(f'ws://example.com/game/{game_id}/connect', body['ws_url'])
                    self.assertEqual(user0, body['players'][0])
                    self.assertEqual(user1, body['players'][1])

            async with session.get(self.server_url(f'/game/{game_id}'), headers={
                'authorization': await self.authorize_test_user(2)
            }) as response:
                self.assertEqual(403, response.status)
                self.assertEqual('403: You are not a part of this game, sorry', await response.text())

    async def test_get_game_state(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
            self.create_test_user(2),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])

        async with aiohttp.ClientSession() as session:
            for user_no in [0, 1]:
                async with session.get(self.server_url(f'/game/{game_id}/state'), headers={
                    'authorization': await self.authorize_test_user(user_no)
                }) as response:
                    self.assertEqual(200, response.status)
                    body = await response.json()
                    self.assertEqual(game_id, body['game_id'])
                    self.assertEqual({
                        'board_size': {
                            'x': 10,
                            'y': 8,
                        },
                    }, body['settings'])

                    tiles = body['board']['tiles']
                    tile = next(iter(tiles.values()))
                    self.assertEqual(0, tile['elevation'])
                    self.assertIsInstance(tile['position']['x'], int)
                    self.assertIsInstance(tile['position']['y'], int)

                    pieces = body['board']['pieces']
                    piece = next(iter(pieces.values()))
                    self.assertIsInstance(piece['owner_id'], str)
                    self.assertIsInstance(piece['tile_id'], str)

            async with session.get(self.server_url(f'/game/{game_id}/state'), headers={
                'authorization': await self.authorize_test_user(2)
            }) as response:
                self.assertEqual(403, response.status)
                self.assertEqual('403: You are not a part of this game, sorry', await response.text())

    async def test_get_game_state_etag(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])

        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url(f'/game/{game_id}/state'), headers={
                'authorization': await self.authorize_test_user(0),
            }) as response:
                self.assertEqual(200, response.status)
                etag = response.headers['etag']
                self.assertIsNotNone(etag)
                body = await response.json()
                self.assertIsNotNone(body)

            async with session.get(self.server_url(f'/game/{game_id}/state'), headers={
                'authorization': await self.authorize_test_user(0),
                'if-none-match': etag,
            }) as response:
                self.assertEqual(304, response.status)
                body = await response.text()
                self.assertEqual('', body)

            game_state = await self.get_game_state(game_id)
            game_state.settings.board_size = (20, 20)
            await self.set_game_state(game_id, game_state)

            async with session.get(self.server_url(f'/game/{game_id}/state'), headers={
                'authorization': await self.authorize_test_user(0),
                'if-none-match': etag,
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertIsNotNone(body)
