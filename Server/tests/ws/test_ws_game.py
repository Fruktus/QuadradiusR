import asyncio
from unittest import IsolatedAsyncioTestCase

import aiohttp
from async_timeout import timeout

from harness import RestTestHarness, TestUserHarness, WebsocketHarness, GameHarness, \
    PowerRandomizerForTests
from quadradiusr_server.constants import QrwsOpcode
from quadradiusr_server.game_state import Piece, Power


class TestWsGame(
    IsolatedAsyncioTestCase,
    WebsocketHarness,
    GameHarness,
    TestUserHarness,
    RestTestHarness,
):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_initial_board(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])
        game_ws = self.server_url(f'/game/{game_id}/connect', protocol='ws')

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(game_ws) as ws0, \
                    session.ws_connect(game_ws) as ws1:
                await asyncio.gather(
                    self.authorize_ws(0, ws0),
                    self.authorize_ws(1, ws1),
                )

                msg0 = await ws0.receive_json()
                self.assertEqual(QrwsOpcode.GAME_STATE, msg0['op'])
                game_state0 = msg0['d']['game_state']
                self.assertIsNotNone(game_state0)
                self.assertIsNotNone(msg0['d']['etag'])
                msg1 = await ws1.receive_json()
                self.assertEqual(QrwsOpcode.GAME_STATE, msg1['op'])
                game_state1 = msg1['d']['game_state']
                self.assertIsNotNone(game_state1)
                self.assertIsNotNone(msg1['d']['etag'])

                self.assertEqual(game_state0, game_state1)

    async def test_turns(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])
        game_ws = self.server_url(f'/game/{game_id}/connect', protocol='ws')

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(game_ws) as ws0, \
                    session.ws_connect(game_ws) as ws1:
                await asyncio.gather(
                    self.authorize_ws(0, ws0),
                    self.authorize_ws(1, ws1),
                )

                msg0 = await ws0.receive_json()
                self.assertEqual(QrwsOpcode.GAME_STATE, msg0['op'])
                game_state = msg0['d']['game_state']

                self.assertEqual(user0['id'], game_state['current_player_id'])

                # user1 cannot make a move
                await self.ws_move(
                    ws1,
                    self.get_game_piece_id_at(game_state, (0, 1)),
                    self.get_game_tile_id_at(game_state, (0, 2)))
                move_result_msg = await self.ws_receive(ws1, QrwsOpcode.MOVE_RESULT)
                self.assertFalse(move_result_msg['d']['is_legal'])
                self.assertEqual('Not your turn', move_result_msg['d']['reason'])

                # user0 makes a move
                await self.ws_move(
                    ws0,
                    self.get_game_piece_id_at(game_state, (0, 1)),
                    self.get_game_tile_id_at(game_state, (0, 2)))
                move_result_msg = await self.ws_receive(ws0, QrwsOpcode.MOVE_RESULT)
                self.assertTrue(move_result_msg['d']['is_legal'])

                gs_diff_msg = await self.ws_receive(ws0, QrwsOpcode.GAME_STATE_DIFF)
                gs_diff = gs_diff_msg['d']['game_state_diff']
                self.assertEqual({
                    self.get_game_piece_id_at(game_state, (0, 1)): {
                        'tile_id': self.get_game_tile_id_at(game_state, (0, 2)),
                    },
                }, gs_diff['board']['pieces'])
                self.assertEqual(user1['id'], gs_diff['current_player_id'])

                game_state = await self.query_game_state(1, game_id)

                # user0 cannot make a move
                await self.ws_move(
                    ws0,
                    self.get_game_piece_id_at(game_state, (0, 2)),
                    self.get_game_tile_id_at(game_state, (0, 3)))
                move_result_msg = await self.ws_receive(ws0, QrwsOpcode.MOVE_RESULT)
                self.assertFalse(move_result_msg['d']['is_legal'])
                self.assertEqual('Not your turn', move_result_msg['d']['reason'])

                # user1 makes a move
                await self.ws_move(
                    ws1,
                    self.get_game_piece_id_at(game_state, (1, 6)),
                    self.get_game_tile_id_at(game_state, (1, 5)))
                move_result_msg = await self.ws_receive(ws1, QrwsOpcode.MOVE_RESULT)
                self.assertTrue(move_result_msg['d']['is_legal'])

    async def test_victory(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])
        game_state = await self.get_game_state(game_id)
        game_state.board.pieces = dict()
        piece0 = Piece(
            id='0',
            owner_id=user0['id'],
            tile_id=game_state.board.get_tile_at(0, 0).id,
        )
        piece1 = Piece(
            id='1',
            owner_id=user1['id'],
            tile_id=game_state.board.get_tile_at(0, 1).id,
        )
        game_state.board.pieces[piece0.id] = piece0
        game_state.board.pieces[piece1.id] = piece1
        await self.set_game_state(game_id, game_state)

        game_ws = self.server_url(f'/game/{game_id}/connect', protocol='ws')

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(game_ws) as ws0, \
                    session.ws_connect(game_ws) as ws1:
                await asyncio.gather(
                    self.authorize_ws(0, ws0),
                    self.authorize_ws(1, ws1),
                )

                game_state = await self.query_game_state(0, game_id)

                # make the final move
                await self.ws_move(
                    ws0,
                    self.get_game_piece_id_at(game_state, (0, 0)),
                    self.get_game_tile_id_at(game_state, (0, 1)))
                move_result_msg = await self.ws_receive(ws0, QrwsOpcode.MOVE_RESULT)
                self.assertTrue(move_result_msg['d']['is_legal'])

                diff_msg = await self.ws_receive(ws0, QrwsOpcode.GAME_STATE_DIFF)
                diff = diff_msg['d']['game_state_diff']
                self.assertEqual(['1'], diff['board']['pieces']['$delete'])
                self.assertEqual(True, diff['finished'])
                self.assertEqual(user0['id'], diff['winner_id'])

                diff_msg = await self.ws_receive(ws1, QrwsOpcode.GAME_STATE_DIFF)
                diff = diff_msg['d']['game_state_diff']
                self.assertEqual(['1'], diff['board']['pieces']['$delete'])
                self.assertEqual(True, diff['finished'])
                self.assertEqual(user0['id'], diff['winner_id'])

    async def test_power_spawn(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])
        game_ws = self.server_url(f'/game/{game_id}/connect', protocol='ws')

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(game_ws) as ws0, \
                    session.ws_connect(game_ws) as ws1:
                await asyncio.gather(
                    self.authorize_ws(0, ws0),
                    self.authorize_ws(1, ws1),
                )

                PowerRandomizerForTests.spawn_next_power(Power(
                    id='power_id',
                    power_definition_id='raise_tile',
                    tile_id='tile_id',
                ))

                msg0 = await ws0.receive_json()
                game_state = msg0['d']['game_state']

                # user0 makes a move
                await self.ws_move(
                    ws0,
                    self.get_game_piece_id_at(game_state, (0, 1)),
                    self.get_game_tile_id_at(game_state, (0, 2)))
                move_result_msg = await self.ws_receive(ws0, QrwsOpcode.MOVE_RESULT)
                self.assertTrue(move_result_msg['d']['is_legal'])

                gs_diff_msg = await self.ws_receive(ws0, QrwsOpcode.GAME_STATE_DIFF)
                self.assertEqual({
                    'board': {
                        'pieces': {
                            self.get_game_piece_id_at(game_state, (0, 1)): {
                                'tile_id': self.get_game_tile_id_at(game_state, (0, 2)),
                            },
                        },
                        'powers': {
                            'power_id': {
                                'authorized_player_ids': [],
                                'power_definition_id': None,
                                'tile_id': 'tile_id',
                                'piece_id': None,
                            },
                        },
                    },
                    'current_player_id': user1['id'],
                }, gs_diff_msg['d']['game_state_diff'])

    async def test_power_capture(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        game_id = await self.create_game(user0['id'], user1['id'])
        game_ws = self.server_url(f'/game/{game_id}/connect', protocol='ws')

        gs = await self.get_game_state(game_id)
        gs.board.powers['power_id'] = Power(
            id='power_id',
            tile_id=gs.board.get_tile_at(0, 2).id,
            power_definition_id='raise_tile',
        )
        await self.set_game_state(game_id, gs)

        async with timeout(2), aiohttp.ClientSession() as session:
            async with session.ws_connect(game_ws) as ws0, \
                    session.ws_connect(game_ws) as ws1:
                await asyncio.gather(
                    self.authorize_ws(0, ws0),
                    self.authorize_ws(1, ws1),
                )

                msg0 = await ws0.receive_json()
                game_state = msg0['d']['game_state']

                # user0 makes a move
                piece_id = self.get_game_piece_id_at(game_state, (0, 1))
                await self.ws_move(
                    ws0,
                    piece_id,
                    self.get_game_tile_id_at(game_state, (0, 2)))
                move_result_msg = await self.ws_receive(ws0, QrwsOpcode.MOVE_RESULT)
                self.assertTrue(move_result_msg['d']['is_legal'])

                gs_diff_msg = await self.ws_receive(ws0, QrwsOpcode.GAME_STATE_DIFF)
                self.assertEqual({
                    'board': {
                        'pieces': {
                            piece_id: {
                                'tile_id': self.get_game_tile_id_at(game_state, (0, 2)),
                            },
                        },
                        'powers': {
                            'power_id': {
                                'authorized_player_ids': [user0['id']],
                                'power_definition_id': 'raise_tile',
                                'tile_id': None,
                                'piece_id': piece_id,
                            },
                        },
                    },
                    'current_player_id': user1['id'],
                }, gs_diff_msg['d']['game_state_diff'])
