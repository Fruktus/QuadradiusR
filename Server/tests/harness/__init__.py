import dataclasses
from abc import ABCMeta

from quadradiusr_server.config import ServerConfig
from quadradiusr_server.db.base import User
from quadradiusr_server.server import QuadradiusRServer


class TestUserHarness(metaclass=ABCMeta):
    __user: User = None

    def get_test_user(self) -> User:
        if not self.__user:
            self.__user = User(
                id_='696969',
                username_='cushy_moconut',
            )

        return self.__user


class RestTestHarness(metaclass=ABCMeta):
    config: ServerConfig
    server: QuadradiusRServer

    async def setup_server(self, config: ServerConfig = ServerConfig(host='', port=0)) -> None:
        self.config = dataclasses.replace(config)
        self.config.host = '127.0.0.1'
        self.config.port = 0
        self.config.database.create_metadata = True
        self.server = QuadradiusRServer(self.config)
        await self.server.start()

    def server_url(self, path: str, *, protocol: str = 'http'):
        return self.server.get_url(protocol) + '/' + path.lstrip('/')

    async def shutdown_server(self):
        await self.server.shutdown()
