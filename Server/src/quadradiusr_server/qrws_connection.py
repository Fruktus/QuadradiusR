from dataclasses import dataclass
from typing import Optional

from aiohttp import WSMsgType
from aiohttp.web_ws import WebSocketResponse

from quadradiusr_server.constants import QrwsOpcode, QrwsCloseCode
from quadradiusr_server.qrws_messages import Message, parse_message, ErrorMessage


@dataclass
class QrwsCloseException(Exception):
    code: int = QrwsCloseCode.OK
    message: str = None


class QrwsConnection:
    """
    A wrapper for QR WS connection.
    """

    def __init__(self, ws: WebSocketResponse) -> None:
        self.ws = ws

    @property
    def closed(self):
        return self.ws.closed

    async def receive_message(self) -> Message:
        while True:
            ws_msg = await self.ws.receive()
            if ws_msg.type == WSMsgType.CLOSE:
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
