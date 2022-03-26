import abc
from abc import ABC

from quadradiusr_server.constants import QrwsOpcode


class Message(ABC):
    def __init__(self, op: int) -> None:
        self.op = op

    def _to_json_data(self):
        return {}

    def to_json(self):
        return {
            'op': self.op,
            'd': self._to_json_data(),
        }


class HeartbeatMessage(Message):
    def __init__(self) -> None:
        super().__init__(QrwsOpcode.HEARTBEAT)


class ErrorMessage(Message):
    def __init__(self, *, message: str, fatal: bool = False) -> None:
        super().__init__(QrwsOpcode.ERROR)
        self.message = message
        self.fatal = fatal

    def _to_json_data(self):
        return {
            'message': self.message,
            'fatal': self.fatal,
        }


class IdentifyMessage(Message):
    def __init__(self, *, token: str) -> None:
        super().__init__(QrwsOpcode.IDENTIFY)
        self.token = token

    def _to_json_data(self):
        return {
            'token': self.token,
        }


class ServerReadyMessage(Message):
    def __init__(self) -> None:
        super().__init__(QrwsOpcode.SERVER_READY)


def parse_message(*, op: int, data: dict) -> Message:
    if op == QrwsOpcode.HEARTBEAT:
        return HeartbeatMessage()
    elif op == QrwsOpcode.ERROR:
        return ErrorMessage(
            message=data['message'],
            fatal=data['fatal'],
        )
    elif op == QrwsOpcode.IDENTIFY:
        return IdentifyMessage(
            token=data['token'],
        )
    else:
        raise ValueError(f'Unknown opcode: {op}')
