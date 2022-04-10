from abc import ABC
from typing import Tuple

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


class NotificationMessage(Message):
    def __init__(self, *, topic: str, data: dict) -> None:
        super().__init__(QrwsOpcode.NOTIFICATION)
        self.topic = topic
        self.data = data

    def _to_json_data(self):
        return {
            'topic': self.topic,
            'data': self.data,
        }


class SubscribeMessage(Message):
    def __init__(self, *, topic: str) -> None:
        super().__init__(QrwsOpcode.SUBSCRIBE)
        self.topic = topic

    def _to_json_data(self):
        return {
            'topic': self.topic,
        }


class SubscribedMessage(Message):
    def __init__(self) -> None:
        super().__init__(QrwsOpcode.SUBSCRIBED)


class SendMessageMessage(Message):
    def __init__(self, *, content: str) -> None:
        super().__init__(QrwsOpcode.SEND_MESSAGE)
        self.content = content

    def _to_json_data(self):
        return {
            'content': self.content,
        }


class KickMessage(Message):
    def __init__(self, *, reason: str) -> None:
        super().__init__(QrwsOpcode.KICK)
        self.reason = reason

    def _to_json_data(self):
        return {
            'reason': self.reason,
        }


class GameStateMessage(Message):
    def __init__(
            self, *, recipient_id: str,
            game_state: dict, etag: str) -> None:
        super().__init__(QrwsOpcode.GAME_STATE)
        self.recipient_id = recipient_id
        self.game_state = game_state
        self.etag = etag

    def _to_json_data(self):
        return {
            'recipient_id': self.recipient_id,
            'game_state': self.game_state,
            'etag': self.etag,
        }


class GameStateDiffMessage(Message):
    def __init__(
            self, *, recipient_id: str,
            game_state_diff: dict,
            etag_from: str, etag_to: str) -> None:
        super().__init__(QrwsOpcode.GAME_STATE_DIFF)
        self.recipient_id = recipient_id
        self.game_state_diff = game_state_diff
        self.etag_from = etag_from
        self.etag_to = etag_to

    def _to_json_data(self):
        return {
            'recipient_id': self.recipient_id,
            'game_state_diff': self.game_state_diff,
            'etag_from': self.etag_from,
            'etag_to': self.etag_to,
        }


class MoveMessage(Message):
    def __init__(
            self, *,
            piece_id: str,
            tile_id: str) -> None:
        super().__init__(QrwsOpcode.MOVE)
        self.piece_id = piece_id
        self.tile_id = tile_id

    def _to_json_data(self):
        return {
            'piece_id': self.piece_id,
            'tile_id': self.tile_id,
        }


class MoveResultMessage(Message):
    def __init__(self, *, is_legal: bool, reason: str) -> None:
        super().__init__(QrwsOpcode.MOVE_RESULT)
        self.is_legal = is_legal
        self.reason = reason

    def _to_json_data(self):
        return {
            'is_legal': self.is_legal,
            'reason': self.reason,
        }


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
    elif op == QrwsOpcode.SUBSCRIBE:
        return SubscribeMessage(
            topic=data['topic'],
        )
    elif op == QrwsOpcode.SEND_MESSAGE:
        return SendMessageMessage(
            content=data['content'],
        )
    elif op == QrwsOpcode.MOVE:
        return MoveMessage(
            piece_id=data['piece_id'],
            tile_id=data['tile_id'],
        )
    else:
        raise ValueError(f'Unknown opcode: {op}')
