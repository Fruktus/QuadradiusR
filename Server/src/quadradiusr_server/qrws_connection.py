from abc import ABC
from dataclasses import dataclass
from typing import Optional, Callable, List

from aiohttp import WSMsgType, web
from aiohttp.abc import BaseRequest
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_ws import WebSocketResponse

from quadradiusr_server.auth import Auth
from quadradiusr_server.constants import QrwsOpcode, QrwsCloseCode
from quadradiusr_server.db.base import User
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transaction_context
from quadradiusr_server.notification import NotificationService, Handler, Notification
from quadradiusr_server.qrws_messages import Message, parse_message, ErrorMessage, ServerReadyMessage, IdentifyMessage, \
    SubscribeMessage, NotificationMessage, SubscribedMessage


@dataclass
class QrwsCloseException(Exception):
    code: int = QrwsCloseCode.OK
    message: str = None


class QrwsConnection:
    """
    A wrapper for QR WS connection.
    """

    def __init__(self, ws: WebSocketResponse = None) -> None:
        self.ws = ws if ws is not None else web.WebSocketResponse()
        self.is_ready = False

    async def prepare(self, request: BaseRequest):
        await self.ws.prepare(request)

    @property
    def closed(self):
        return self.ws.closed

    async def authorize(self, auth: Auth, repository: Repository):
        identify_msg = await self.receive_message()
        if not isinstance(identify_msg, IdentifyMessage):
            await self.send_error(
                'Please identify yourself',
                close_code=QrwsCloseCode.UNAUTHORIZED)
            raise HTTPUnauthorized()

        user_id = auth.authenticate(identify_msg.token)
        if user_id is None:
            await self.send_error(
                'Auth failed',
                close_code=QrwsCloseCode.UNAUTHORIZED)
            raise HTTPUnauthorized()
        user = await repository.user_repository.get_by_id(user_id)

        return user

    async def ready(self):
        if not self.is_ready:
            self.is_ready = True
            await self.send_message(ServerReadyMessage())

    async def receive_message(self) -> Message:
        while True:
            ws_msg = await self.ws.receive()
            if ws_msg.type in {
                WSMsgType.ERROR, WSMsgType.CLOSING,
                WSMsgType.CLOSE, WSMsgType.CLOSED
            }:
                raise QrwsCloseException()
            elif ws_msg.type != WSMsgType.TEXT:
                await self.send_error('Unexpected message type')
                continue

            data = ws_msg.json()

            if 'op' not in data:
                await self.send_error('Missing operation')
                continue

            if 'd' not in data:
                await self.send_error('Missing data')
                continue

            op = data['op']
            try:
                return parse_message(op=QrwsOpcode(op), data=data['d'])
            except ValueError | KeyError as e:
                await self.send_error(f'Malformed data: {e}')
                continue

    async def send_message(self, message: Message):
        await self.ws.send_json(message.to_json())

    async def send_error(self, message: str, *, close_code: Optional[int] = None):
        await self.send_message(ErrorMessage(
            message=message,
            fatal=close_code is not None))
        if close_code is not None:
            await self.ws.close(code=close_code, message=message.encode())

    async def close(self, code: int, message: str) -> bool:
        return await self.ws.close(
            code=code,
            message=message.encode() if message else None)


class BasicConnection(ABC):
    def __init__(
            self, qrws: QrwsConnection, user: User,
            notification_service: NotificationService,
            database: DatabaseEngine) -> None:
        super().__init__()
        self._qrws = qrws
        self._user = user
        self._notification_service = notification_service
        self._database = database
        self._close_handlers: List[Callable[[], None]] = []

    @property
    def qrws(self) -> QrwsConnection:
        return self._qrws

    @property
    def user(self) -> User:
        return self._user

    @property
    def notification_service(self) -> NotificationService:
        return self._notification_service

    async def handle_connection(self):
        qrws = self.qrws
        await qrws.ready()
        try:
            while not qrws.closed:
                message = await qrws.receive_message()
                async with transaction_context(self._database):
                    handled = await self.handle_message(message)
                if not handled:
                    await qrws.send_message(ErrorMessage(
                        message='Unexpected opcode', fatal=False))
        except QrwsCloseException as e:
            await qrws.close(
                code=e.code,
                message=e.message)
        finally:
            for handler in self._close_handlers:
                handler()

    def add_close_handler(self, handler: Callable[[], None]):
        self._close_handlers.append(handler)

    async def handle_message(self, message: Message) -> bool:
        qrws = self.qrws
        user = self.user
        ns = self.notification_service

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

            sub_handler = SubscribeHandler()
            ns.register_handler(
                user.id_, sub_handler)
            self.add_close_handler(lambda: ns.unregister_handler(sub_handler))
            await qrws.send_message(SubscribedMessage())
            return True
        else:
            return False
