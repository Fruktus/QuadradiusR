from quadradiusr_server.db.base import User
from quadradiusr_server.qrws_connection import BasicConnection
from quadradiusr_server.qrws_messages import Message


class GatewayConnection(BasicConnection):
    async def handle_message(self, user: User, message: Message) -> bool:
        if await super().handle_message(user, message):
            return True

        return False
