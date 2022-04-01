from quadradiusr_server.qrws_connection import BasicConnection
from quadradiusr_server.qrws_messages import Message


class GatewayConnection(BasicConnection):
    async def handle_message(self, message: Message) -> bool:
        if await super().handle_message(message):
            return True

        return False
