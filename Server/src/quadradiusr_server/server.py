from typing import Optional

import aiohttp.web
from aiohttp.web_runner import AppRunner, TCPSite

from quadradiusr_server.config import ServerConfig


class QuadradiusRServer:
    def __init__(self, config: ServerConfig) -> None:
        self.config: ServerConfig = config
        self.app = aiohttp.web.Application()
        self.app.router.add_route('GET', '/health', self.handle_health)

        self.runner: Optional[AppRunner] = None
        self.site: Optional[TCPSite] = None

    async def handle_health(self, request):
        return aiohttp.web.json_response({
            'status': 'up',
        })

    @property
    def url(self) -> Optional[str]:
        if not self.site:
            return None

        # TCPSite.name is not implemented properly
        addr = self.site._server.sockets[0].getsockname()
        scheme = "https" if self.site._ssl_context else "http"
        return f'{scheme}://{addr[0]}:{addr[1]}'

    async def start(self):
        self.runner = AppRunner(self.app)

        await self.runner.setup()

        cfg = self.config
        self.site = TCPSite(
            runner=self.runner,
            host=cfg.host,
            port=cfg.port,
            shutdown_timeout=cfg.shutdown_timeout,
            backlog=cfg.backlog,
            reuse_address=cfg.reuse_address,
            reuse_port=cfg.reuse_port,
            # TODO ssl_context=ssl_context,
        )

        await self.site.start()

    async def shutdown(self):
        if self.runner:
            await self.runner.cleanup()
