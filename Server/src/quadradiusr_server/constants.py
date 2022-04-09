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
    KICK = 7
    SEND_MESSAGE = 8
    GAME_STATE = 9
    GAME_STATE_DIFF = 10


class QrwsCloseCode(IntEnum):
    OK = WSCloseCode.OK
    MALFORMED_MESSAGE = 4000
    UNAUTHORIZED = 4001
    CONFLICT = 4002
