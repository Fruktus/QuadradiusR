from quadradiusr_server.auth import User
from quadradiusr_server.notification import Handler, Notification
from quadradiusr_server.qrws_connection import QrwsConnection
from quadradiusr_server.qrws_messages import Message, ErrorMessage, SubscribeMessage, NotificationMessage, \
    SubscribedMessage
from quadradiusr_server.server import QuadradiusRServer


class GatewayConnection:
    def __init__(
            self, server: QuadradiusRServer,
            qrws: QrwsConnection, user: User) -> None:
        super().__init__()
        self._server = server
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
        server = self._server
        qrws = self._qrws
        user = self._user

        if isinstance(message, SubscribeMessage):
            topic = message.topic

            class SubscribeHandler(Handler):
                def get_topic(self):
                    return topic

                async def handle(self, notification: Notification):
                    await qrws.send_message(NotificationMessage(
                        topic=topic,
                        data=notification.data,
                    ))

            server.notification_service.register_handler(
                user.id_, SubscribeHandler())
            await qrws.send_message(SubscribedMessage())
        else:
            await qrws.send_message(ErrorMessage(
                message='Unexpected opcode', fatal=False))
