import datetime
import uuid
from unittest import IsolatedAsyncioTestCase

from harness import RestTestHarness, TestUserHarness, NotificationHandlerForTests
from quadradiusr_server.db.base import GameInvite
from quadradiusr_server.db.transactions import transaction_context
from quadradiusr_server.notification import Notification


class TestCron(IsolatedAsyncioTestCase, TestUserHarness, RestTestHarness):

    async def asyncSetUp(self) -> None:
        await self.setup_server()

    async def asyncTearDown(self) -> None:
        await self.shutdown_server()

    async def test_purge_game_invites(self):
        await self.create_test_user(0)
        await self.create_test_user(1)

        user0 = await self.get_test_user(0)
        user1 = await self.get_test_user(1)

        nh0 = NotificationHandlerForTests()
        nh1 = NotificationHandlerForTests()
        self.server.notification_service.register_handler(user0['id'], nh0)
        self.server.notification_service.register_handler(user1['id'], nh1)

        game_invite_id = str(uuid.uuid4())
        async with transaction_context(self.server.database):
            gi = GameInvite(
                id_=game_invite_id,
                from_id_=user0['id'],
                subject_id_=user1['id'],
                expiration_=(datetime.datetime.now() - datetime.timedelta(seconds=10)),
            )
            await self.server.repository.game_invite_repository.add(gi)
            gi = GameInvite(
                id_=str(uuid.uuid4()),
                from_id_=user0['id'],
                subject_id_=user1['id'],
                expiration_=(datetime.datetime.now() + datetime.timedelta(seconds=10)),
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
