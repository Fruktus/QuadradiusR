from aiohttp import web

from quadradiusr_server.auth import Auth
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.gateway import GatewayConnection
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import QrwsConnection
from quadradiusr_server.server import routes, QuadradiusRServer
from quadradiusr_server.utils import is_request_websocket_upgradable


@routes.view('/gateway')
class GatewayView(web.View):
    @transactional
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        auth: Auth = self.request.app['auth']
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']

        if not is_request_websocket_upgradable(self.request):
            return web.json_response({
                'url': server.get_href('ws') + '/gateway',
            })

        qrws = QrwsConnection()
        await qrws.prepare(self.request)
        user = await qrws.authorize(auth, repository)

        gateway = GatewayConnection(qrws, user, ns, repository)
        server.register_gateway(gateway)
        try:
            await gateway.handle_connection()
            return qrws.ws
        finally:
            server.unregister_gateway(gateway)
