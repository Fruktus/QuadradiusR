import asyncio
from collections import defaultdict
from typing import Optional, Mapping, List

from aiohttp import web
from aiohttp.web_runner import AppRunner, TCPSite

from quadradiusr_server.auth import Auth
from quadradiusr_server.config import ServerConfig
from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.utils import import_submodules

routes = web.RouteTableDef()


class ServerNotStartedException(Exception):
    pass


class QuadradiusRServer:
    def __init__(self, config: ServerConfig) -> None:
        self.gateway_connections: Mapping[str, List[object]] = \
            defaultdict(lambda: [])
        self.notification_service = NotificationService()
        self.database = DatabaseEngine(config.database)
        self.repository = Repository(self.database)
        self.auth = Auth(config.auth, self.repository)
        self.config: ServerConfig = config
        self.app = web.Application()
        self.app['server'] = self
        self.app['auth'] = self.auth
        self.app['database'] = self.database
        self.app['repository'] = self.repository
        self.app['notification'] = self.notification_service
        self.app.add_routes(routes)

        self.runner: Optional[AppRunner] = None
        self.site: Optional[TCPSite] = None

    def _ensure_started(self):
        if not self.site:
            raise ServerNotStartedException()

    @property
    def is_secure(self) -> bool:
        self._ensure_started()

        return True if self.site._ssl_context else False

    @property
    def address(self) -> (str, int):
        self._ensure_started()

        return self.site._server.sockets[0].getsockname()

    def _get_scheme(self, protocol):
        if protocol == 'http':
            scheme = 'https' if self.is_secure else 'http'
        elif protocol == 'ws':
            scheme = 'wss' if self.is_secure else 'ws'
        else:
            raise ValueError(f'Unknown protocol {protocol}')
        return scheme

    def get_url(self, protocol: str = 'http') -> str:
        # TCPSite.name is not implemented properly
        self._ensure_started()

        addr = self.address
        scheme = self._get_scheme(protocol)

        return f'{scheme}://{addr[0]}:{addr[1]}'

    def get_href(self, protocol: str = 'http') -> str:
        if self.config.href:
            return f'{self._get_scheme(protocol)}://{self.config.href}'
        else:
            return self.get_url(protocol)

    async def start(self):
        await self.database.initialize()

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
        if self.database:
            await self.database.dispose()

    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.start())
        loop.close()

    def register_gateway(self, gateway):
        user = gateway.user
        self.gateway_connections[user.id_].append(gateway)

    def unregister_gateway(self, gateway):
        user = gateway.user
        self.gateway_connections[user.id_].remove(gateway)


# importing submodules automatically registers endpoints
import quadradiusr_server.rest
import_submodules(quadradiusr_server.rest)
