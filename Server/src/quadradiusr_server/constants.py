from enum import IntEnum

from aiohttp import WSCloseCode


class QrwsOpcode(IntEnum):
    HEARTBEAT = 0
    ERROR = 1
    IDENTIFY = 2
    SERVER_READY = 3
    NOTIFICATION = 4
    SUBSCRIBE = 5
    SUBSCRIBED = 6
    SEND_MESSAGE = 7
    MESSAGE_SENT = 6
    KICK = 7


class QrwsCloseCode(IntEnum):
    OK = WSCloseCode.OK
    MALFORMED_MESSAGE = 4000
    UNAUTHORIZED = 4001
    CONFLICT = 4002
