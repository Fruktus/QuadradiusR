import asyncio
import datetime
import uuid
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from harness import RestTestHarness, TestUserHarness, NotificationHandlerForTests
from quadradiusr_server.db.base import GameInvite
from quadradiusr_server.db.transactions import transaction_context
from quadradiusr_server.notification import Notification
from quadradiusr_server.server import QuadradiusRServer


class TestCron(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        def sc(server: QuadradiusRServer):
            # prevent automatic execution
            server.cron.register = AsyncMock()
            server.setup_service.run_setup_jobs = AsyncMock()
        await self.setup_server(server_configurator=sc)

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_purge_game_invites(self):
        await asyncio.gather(
            self.create_test_user(0),
            self.create_test_user(1),
        )

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        nh0 = NotificationHandlerForTests()
        nh1 = NotificationHandlerForTests()
        self.server.notification_service.register_handler(user0['id'], nh0)
        self.server.notification_service.register_handler(user1['id'], nh1)

        game_invite_id = str(uuid.uuid4())
        async with transaction_context(self.server.database):
            now = datetime.datetime.now(datetime.timezone.utc)
            gi = GameInvite(
                id_=game_invite_id,
                from_id_=user0['id'],
                subject_id_=user1['id'],
                expires_at_=(now - datetime.timedelta(seconds=10)),
            )
            await self.server.repository.game_invite_repository.add(gi)
            gi = GameInvite(
                id_=str(uuid.uuid4()),
                from_id_=user0['id'],
                subject_id_=user1['id'],
                expires_at_=(now + datetime.timedelta(seconds=10)),
            )
            await self.server.repository.game_invite_repository.add(gi)

        await self.server.cron._purge_game_invites()

        await NotificationHandlerForTests.receive_now()
        self.assertEqual(1, len(nh0.notifications))
        self.assertEqual(1, len(nh1.notifications))

        expected_n0 = Notification(
            topic='game.invite.removed',
            subject_id=user0['id'],
            data={
                'game_invite_id': game_invite_id,
                'reason': 'expired',
            },
        )
        self.assertEqual(expected_n0, nh0.notifications[0])

        expected_n1 = Notification(
            topic='game.invite.removed',
            subject_id=user1['id'],
            data={
                'game_invite_id': game_invite_id,
                'reason': 'expired',
            },
        )
        self.assertEqual(expected_n1, nh1.notifications[0])

    async def test_create_main_lobby(self):
        await self.create_test_user(0)

        lobby_repo = self.server.repository.lobby_repository
        async with transaction_context(self.server.database):
            main_lobby = await lobby_repo.get_by_id('@main')
            self.assertIsNone(main_lobby)

        await self.server.setup_service._create_main_lobby()

        async with transaction_context(self.server.database):
            main_lobby = await lobby_repo.get_by_id('@main')
            self.assertIsNotNone(main_lobby)
