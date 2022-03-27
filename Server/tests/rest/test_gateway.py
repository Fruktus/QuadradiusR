from unittest import IsolatedAsyncioTestCase

import aiohttp
from aiohttp import WSMsgType
from async_timeout import timeout

from quadradiusr_server.auth import User
from quadradiusr_server.config import ServerConfig
from quadradiusr_server.constants import QrwsOpcode, QrwsCloseCode
from .harness import RestTestHarness


class TestGateway(IsolatedAsyncioTestCase, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server(ServerConfig(
            host='',
            port=0,
            href='example.com',
        ))

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_gateway_info(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.server_url('/gateway')) as response:
                self.assertEqual(200, response.status)

                body = await response.json()
                self.assertEqual('ws://example.com/gateway', body['url'])

    async def test_gateway_without_identify(self):
        async with timeout(2):
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.server_url(
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
        async with timeout(2):
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.server_url(
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
        async with timeout(2):
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.server_url(
                        '/gateway', protocol='ws')) as ws:
                    await ws.send_json({
                        'op': QrwsOpcode.IDENTIFY,
                        'd': {
                            'token': self.server.auth.issue_token(User('1234')),
                        },
                    })
                    data = await ws.receive_json()
                    self.assertEqual(QrwsOpcode.SERVER_READY, data['op'])
