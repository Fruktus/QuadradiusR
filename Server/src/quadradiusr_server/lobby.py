import datetime
import logging
import uuid
from typing import Dict, List

from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import User, LobbyMessage
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.notification import NotificationService, Notification
from quadradiusr_server.qrws_connection import BasicConnection, QrwsConnection
from quadradiusr_server.qrws_messages import Message, SendMessageMessage, KickMessage
from quadradiusr_server.rest.mappers import lobby_message_to_json


class LiveLobby:
    def __init__(
            self, lobby_id: str, repository: Repository,
            ns: NotificationService) -> None:
        self.lobby_id = lobby_id
        self.repository = repository
        self.ns = ns

        self._players: Dict[str, LobbyConnection] = {}

    @property
    def player_ids(self) -> List[str]:
        return [conn.user_id for conn in self._players.values()]

    async def get_players(self) -> List[User]:
        user_repo = self.repository.user_repository
        return await user_repo.get_by_ids(self.player_ids)

    async def join(self, lobby_conn: 'LobbyConnection'):
        user_repo = self.repository.user_repository
        user_id = lobby_conn.user_id
        user = await user_repo.get_by_id(user_id)

        if user_id in self._players:
            await self._players[user_id].kick()
        self._players[user_id] = lobby_conn

        subjects = set(self._players.keys()) - {user_id}
        for subject_id in subjects:
            self.ns.notify(Notification(
                topic='lobby.joined',
                subject_id=subject_id,
                data={
                    'lobby_id': self.lobby_id,
                    'user': {
                        'id': user.id_,
                        'username': user.username_,
                    },
                },
            ))
        logging.info(f'User {user.friendly_name} joined lobby {lobby_conn.lobby.lobby_id}')

    async def leave(self, lobby_conn: 'LobbyConnection'):
        user_id = lobby_conn.user_id
        if lobby_conn in self._players.values():
            del self._players[user_id]

        subjects = set(self._players.keys())
        for subject_id in subjects:
            self.ns.notify(Notification(
                topic='lobby.left',
                subject_id=subject_id,
                data={
                    'lobby_id': self.lobby_id,
                    'user_id': user_id,
                },
            ))
        logging.info(f'User {user_id} left lobby {lobby_conn.lobby.lobby_id}')

    async def send_message(self, user: User, content: str):
        lobby_repo = self.repository.lobby_repository
        lobby = await lobby_repo.get_by_id(self.lobby_id)
        lobby_message = LobbyMessage(
            id_=str(uuid.uuid4()),
            user_id_=user.id_,
            user_=user,
            lobby_id_=self.lobby_id,
            lobby_=lobby,
            content_=content,
            created_at_=datetime.datetime.now(datetime.timezone.utc),
        )
        await lobby_repo.add_message(lobby_message)
        for subject_id in self._players.keys():
            self.ns.notify(Notification(
                topic='lobby.message.received',
                subject_id=subject_id,
                data={
                    'message': lobby_message_to_json(lobby_message),
                },
            ))
        logging.info(f'Message by {user.friendly_name} in {lobby.id_}: {content}')

    def joined(self, user: User):
        return user.id_ in self._players.keys()


class LobbyConnection(BasicConnection):

    def __init__(
            self, lobby: LiveLobby,
            qrws: QrwsConnection,
            user: User,
            notification_service: NotificationService,
            repository: Repository) -> None:
        super().__init__(qrws, user, notification_service, repository)
        self.lobby: LiveLobby = lobby

    async def handle_message(self, user: User, message: Message) -> bool:
        if await super().handle_message(user, message):
            return True

        if isinstance(message, SendMessageMessage):
            content = message.content
            await self.lobby.send_message(user, content)
            return True
        else:
            return False

    async def kick(self):
        await self.qrws.send_message(KickMessage(
            reason='Connected from another location',
        ))
        await self.qrws.close(
            QrwsCloseCode.CONFLICT,
            'Connected from another location')
