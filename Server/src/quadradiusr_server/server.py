import aiohttp.web

from quadradiusr_server.config import ServerConfig


class QuadradiusRServer:
    def __init__(self, config: ServerConfig) -> None:
        self.config: ServerConfig = config

    async def run(self):
        pass