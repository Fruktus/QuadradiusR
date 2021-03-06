from unittest import IsolatedAsyncioTestCase

import aiohttp
from aiohttp import WSMsgType
from async_timeout import timeout

from harness import TestUserHarness, RestTestHarness
from quadradiusr_server.constants import QrwsOpcode, QrwsCloseCode


class TestWsGateway(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_gateway_without_identify(self):
        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/gateway', protocol='ws')) as ws:
            await ws.send_json({
                'op': QrwsOpcode.HEARTBEAT,
                'd': {},
            })
            data = await ws.receive_json()
            self.assertEqual(QrwsOpcode.ERROR, data['op'])
            self.assertEqual('Please identify yourself', data['d']['message'])
            self.assertEqual(True, data['d']['fatal'])

            received = await ws.receive()
            self.assertEqual(WSMsgType.CLOSE, received.type)
            self.assertEqual(QrwsCloseCode.UNAUTHORIZED, received.data)
            self.assertEqual('Please identify yourself', received.extra)
            self.assertTrue(ws.closed)

    async def test_gateway_auth_fail(self):
        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/gateway', protocol='ws')) as ws:
            await ws.send_json({
                'op': QrwsOpcode.IDENTIFY,
                'd': {
                    'token': 'xyz',
                },
            })
            data = await ws.receive_json()
            self.assertEqual(QrwsOpcode.ERROR, data['op'])
            self.assertEqual('Auth failed', data['d']['message'])
            self.assertEqual(True, data['d']['fatal'])

            received = await ws.receive()
            self.assertEqual(WSMsgType.CLOSE, received.type)
            self.assertEqual(QrwsCloseCode.UNAUTHORIZED, received.data)
            self.assertEqual('Auth failed', received.extra)
            self.assertTrue(ws.closed)

    async def test_gateway_auth_pass(self):
        await self.create_test_user(0)
        async with timeout(2), \
                aiohttp.ClientSession() as session, \
                session.ws_connect(self.server_url(
                    '/gateway', protocol='ws')) as ws:
            await ws.send_json({
                'op': QrwsOpcode.IDENTIFY,
                'd': {
                    'token': await self.authorize_test_user(0),
                },
            })
            data = await ws.receive_json()
            self.assertEqual(QrwsOpcode.SERVER_READY, data['op'])
