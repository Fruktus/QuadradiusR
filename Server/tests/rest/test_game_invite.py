import datetime
import re
from unittest import IsolatedAsyncioTestCase

import aiohttp

from harness import RestTestHarness, TestUserHarness


class TestGameInvite(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_create_invite(self):
        await self.create_test_user(0)
        await self.create_test_user(1)
        await self.create_test_user(2)

        user1 = await self.get_test_user(1)

        async with aiohttp.ClientSession() as session:
            exp = datetime.datetime.now() + datetime.timedelta(seconds=60)
            async with session.post(self.server_url('/game_invite'), json={
                'subject_id': user1['id'],
                'expiration': exp.isoformat(),
            }, headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(201, response.status)
                loc = response.headers['location']
                self.assertRegex(loc, '/game_invite/[^/]+')

            game_invite_id = re.match('/game_invite/(.*)', loc).group(1)

            async with session.get(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(0),
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual(game_invite_id, body['id'])

            async with session.get(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(1),
            }) as response:
                self.assertEqual(200, response.status)
                body = await response.json()
                self.assertEqual(game_invite_id, body['id'])

            async with session.get(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(2),
            }) as response:
                self.assertEqual(403, response.status)
                self.assertEqual(
                    '403: You are not a part of the invite',
                    await response.text())

    async def test_create_invite_to_oneself(self):
        await self.create_test_user(0)
        user0 = await self.get_test_user(0)

        async with aiohttp.ClientSession() as session:
            exp = datetime.datetime.now() + datetime.timedelta(seconds=60)
            async with session.post(self.server_url('/game_invite'), json={
                'subject': user0['id'],
                'expiration': exp.isoformat(),
            }, headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(400, response.status)
                self.assertEqual(
                    '400: User cannot invite themselves... or can they?',
                    await response.text())

    async def test_create_invite_exp_in_past(self):
        await self.create_test_user(0)
        await self.create_test_user(1)
        user1 = await self.get_test_user(1)

        async with aiohttp.ClientSession() as session:
            exp = datetime.datetime.now() - datetime.timedelta(seconds=60)
            async with session.post(self.server_url('/game_invite'), json={
                'subject': user1['id'],
                'expiration': exp.isoformat(),
            }, headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(400, response.status)
                self.assertEqual(
                    '400: Invite cannot expire in the past',
                    await response.text())

    async def test_create_invite_exp_too_late(self):
        await self.create_test_user(0)
        await self.create_test_user(1)
        user1 = await self.get_test_user(1)

        async with aiohttp.ClientSession() as session:
            exp = datetime.datetime.now() + datetime.timedelta(days=1000)
            async with session.post(self.server_url('/game_invite'), json={
                'subject': user1['id'],
                'expiration': exp.isoformat(),
            }, headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(400, response.status)
                self.assertEqual(
                    '400: Expiration date too late',
                    await response.text())

    async def test_create_invite_nonexisting_user(self):
        await self.create_test_user(0)

        async with aiohttp.ClientSession() as session:
            exp = datetime.datetime.now() + datetime.timedelta(seconds=60)
            async with session.post(self.server_url('/game_invite'), json={
                'subject': 'asasdasd',
                'expiration': exp.isoformat(),
            }, headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(400, response.status)
                self.assertEqual(
                    '400: Subject not found',
                    await response.text())

    async def test_delete_invite(self):
        await self.create_test_user(0)
        await self.create_test_user(1)
        await self.create_test_user(2)

        user1 = await self.get_test_user(1)

        async with aiohttp.ClientSession() as session:
            exp = datetime.datetime.now() + datetime.timedelta(seconds=60)
            async with session.post(self.server_url('/game_invite'), json={
                'subject_id': user1['id'],
                'expiration': exp.isoformat(),
            }, headers={
                'authorization': await self.authorize_test_user(0)
            }) as response:
                self.assertEqual(201, response.status)
                loc = response.headers['location']

            async with session.get(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(0),
            }) as response:
                self.assertEqual(200, response.status)

            async with session.get(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(2),
            }) as response:
                self.assertEqual(403, response.status)
                self.assertEqual(
                    '403: You are not a part of the invite',
                    await response.text())

            async with session.delete(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(1),
            }) as response:
                self.assertEqual(204, response.status)

            async with session.get(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(0),
            }) as response:
                self.assertEqual(404, response.status)
                self.assertEqual(
                    '404: Game invite not found',
                    await response.text())

            async with session.get(self.server_url(loc), headers={
                'authorization': await self.authorize_test_user(2),
            }) as response:
                self.assertEqual(404, response.status)
                self.assertEqual(
                    '404: Game invite not found',
                    await response.text())
