import asyncio
import logging

from quadradiusr_server.config import CronConfig
from quadradiusr_server.db.base import Lobby
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transaction_context
from quadradiusr_server.notification import NotificationService, Notification


class Cron:
    def __init__(
            self, config: CronConfig, repository: Repository,
            notification_service: NotificationService) -> None:
        self.config = config
        self.repository = repository
        self.ns = notification_service

    async def register(self):
        logging.info('Registering cron jobs')
        asyncio.create_task(self._cron_purge_game_invites())
        asyncio.create_task(self._cron_purge_tokens())
        logging.info('Cron jobs registered')

    async def _cron_purge_game_invites(self):
        logging.debug('Purging game invites')
        while True:
            await asyncio.sleep(self.config.purge_game_invites_delay)
            await self._purge_game_invites()

    async def _purge_game_invites(self):
        async with transaction_context(self.repository.database):
            gi_repo = self.repository.game_invite_repository
            old_invites = await gi_repo.get_old_invites()
            for invite in old_invites:
                await gi_repo.remove(invite)
                for subject_id in [invite.from_id_, invite.subject_id_]:
                    await self.repository.synchronize_transaction_on_commit(
                        self.ns.notify_now(Notification(
                            topic='game.invite.removed',
                            subject_id=subject_id,
                            data={
                                'game_invite_id': invite.id_,
                                'reason': 'expired',
                            },
                        )))

    async def _cron_purge_tokens(self):
        logging.debug('Purging game invites')
        while True:
            await asyncio.sleep(self.config.purge_tokens_delay)
            await self._purge_tokens()

    async def _purge_tokens(self):
        async with transaction_context(self.repository.database):
            at_repo = self.repository.access_token_repository
            await at_repo.remove_old_tokens()
        logging.debug('Tokens purged')


class SetupService:
    def __init__(
            self, repository: Repository) -> None:
        self.repository = repository

    async def run_setup_jobs(self):
        logging.info('Running setup jobs')
        await self._create_main_lobby()
        logging.info('Setup jobs finished')

    async def _create_main_lobby(self):
        logging.debug('Creating main lobby')
        async with transaction_context(self.repository.database):
            lobby_repo = self.repository.lobby_repository
            if await lobby_repo.get_by_id('@main') is None:
                main = Lobby(
                    id_='@main',
                    name_='Main',
                )
                await lobby_repo.add(main)
        logging.debug('Main lobby created')
