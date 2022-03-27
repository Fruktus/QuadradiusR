from quadradiusr_server.auth import User
from quadradiusr_server.qrws_connection import QrwsConnection
from quadradiusr_server.qrws_messages import Message


class GatewayConnection:
    def __init__(self, qrws: QrwsConnection, user: User) -> None:
        super().__init__()
        self._qrws = qrws
        self._user = user

    @property
    def user(self) -> User:
        return self._user

    async def handle_connection(self):
        qrws = self._qrws
        while not qrws.closed:
            message = await qrws.receive_message()
            await self.handle_message(message)

    async def handle_message(self, message: Message):
        # TODO handle gateway messages
        pass
