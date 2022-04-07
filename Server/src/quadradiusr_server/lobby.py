import datetime
import uuid
from typing import Dict, List

from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Lobby, User, LobbyMessage
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.notification import NotificationService, Notification
from quadradiusr_server.qrws_connection import BasicConnection, QrwsConnection
from quadradiusr_server.qrws_messages import Message, SendMessageMessage, MessageSentMessage, KickMessage


class LiveLobby:
    def __init__(
            self, lobby: Lobby, repository: Repository,
            ns: NotificationService) -> None:
        self.lobby = lobby
        self.repository = repository
        self.ns = ns

        self._players: Dict[str, LobbyConnection] = {}

    @property
    def players(self) -> List[User]:
        return [conn.user for conn in self._players.values()]

    async def join(self, lobby_conn: 'LobbyConnection'):
        user_id = lobby_conn.user.id_
        if user_id in self._players:
            await self._players[user_id].kick()
        self._players[user_id] = lobby_conn

        subjects = set(self._players.keys()) - {user_id}
        for subject_id in subjects:
            self.ns.notify(Notification(
                topic='lobby.joined',
                subject_id=subject_id,
                data={
                    'lobby_id': self.lobby.id_,
                    'user': {
                        'id': user_id,
                        'username': lobby_conn.user.username_,
                    },
                },
            ))

    async def leave(self, lobby_conn: 'LobbyConnection'):
        user_id = lobby_conn.user.id_
        if lobby_conn in self._players.values():
            del self._players[user_id]

        subjects = set(self._players.keys())
        for subject_id in subjects:
            self.ns.notify(Notification(
                topic='lobby.left',
                subject_id=subject_id,
                data={
                    'lobby_id': self.lobby.id_,
                    'user_id': user_id,
                },
            ))

    async def send_message(self, user: User, content: str):
        lobby_repo = self.repository.lobby_repository
        lobby_message = LobbyMessage(
            id_=str(uuid.uuid4()),
            user_id_=user.id_,
            lobby_id_=self.lobby.id_,
            content_=content,
            created_at_=datetime.datetime.now(datetime.timezone.utc),
        )
        await lobby_repo.add_message(lobby_message)
        for conn in self._players.values():
            await conn.message_sent(user, content)

    def joined(self, user: User):
        return user.id_ in self._players.keys()


class LobbyConnection(BasicConnection):

    def __init__(
            self, lobby: LiveLobby,
            qrws: QrwsConnection,
            user: User,
            notification_service: NotificationService,
            database: DatabaseEngine) -> None:
        super().__init__(qrws, user, notification_service, database)
        self.lobby: LiveLobby = lobby

    async def handle_message(self, message: Message) -> bool:
        if await super().handle_message(message):
            return True

        if isinstance(message, SendMessageMessage):
            content = message.content
            await self.lobby.send_message(self.user, content)
            return True
        else:
            return False

    async def message_sent(self, user, content):
        await self.qrws.send_message(MessageSentMessage(
            user_id=user.id_,
            content=content,
        ))

    async def kick(self):
        await self.qrws.send_message(KickMessage(
            reason='Connected from another location',
        ))
        await self.qrws.close(
            QrwsCloseCode.CONFLICT,
            'Connected from another location')
