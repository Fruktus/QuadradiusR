from enum import IntEnum

from aiohttp import WSCloseCode


class QrwsOpcode(IntEnum):
    HEARTBEAT = 0
    ERROR = 1
    IDENTIFY = 2
    SERVER_READY = 3


class QrwsCloseCode(IntEnum):
    OK = WSCloseCode.OK
    MALFORMED_MESSAGE = 4000
    UNAUTHORIZED = 4001
