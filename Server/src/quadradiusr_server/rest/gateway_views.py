from aiohttp import web

from quadradiusr_server.auth import Auth
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.gateway import GatewayConnection
from quadradiusr_server.qrws_connection import QrwsConnection, QrwsCloseException
from quadradiusr_server.server import routes, QuadradiusRServer


@routes.view('/gateway')
class GatewayView(web.View):
    @transactional
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        auth: Auth = self.request.app['auth']
        repository: Repository = self.request.app['repository']

        if 'connection' not in self.request.headers or \
                'upgrade' not in self.request.headers['connection']:
            return web.json_response({
                'url': server.get_href('ws') + '/gateway',
            })

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        try:
            qrws = QrwsConnection(ws)
            user = await qrws.handshake(auth, repository)

            gateway = GatewayConnection(server, qrws, user)
            server.register_gateway(gateway)
            try:
                await gateway.handle_connection()
            finally:
                server.unregister_gateway(gateway)
            return ws
        except QrwsCloseException as e:
            await ws.close(
                code=e.code,
                message=e.message.encode() if e.message else None)
            return ws
