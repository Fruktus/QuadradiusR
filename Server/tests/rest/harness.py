import dataclasses
from abc import ABCMeta

from quadradiusr_server.config import ServerConfig
from quadradiusr_server.server import QuadradiusRServer


class RestTestHarness(metaclass=ABCMeta):
    config: ServerConfig
    server: QuadradiusRServer

    async def setup_server(self, config: ServerConfig = ServerConfig(host='', port=0)) -> None:
        self.config = dataclasses.replace(config)
        self.config.host = '127.0.0.1'
        self.config.port = 0
        self.server = QuadradiusRServer(self.config)
        await self.server.start()

    def server_url(self, path: str):
        return self.server.url + '/' + path.lstrip('/')

    async def shutdown_server(self):
        await self.server.shutdown()
