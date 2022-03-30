from aiohttp import web

from quadradiusr_server.auth import Auth
from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.gateway import GatewayConnection
from quadradiusr_server.qrws_connection import QrwsConnection, QrwsCloseException
from quadradiusr_server.qrws_messages import IdentifyMessage, ServerReadyMessage
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

            identify_msg = await qrws.receive_message()
            if not isinstance(identify_msg, IdentifyMessage):
                await qrws.send_error(
                    'Please identify yourself',
                    close_code=QrwsCloseCode.UNAUTHORIZED)
                return ws

            user_id = auth.authenticate(identify_msg.token)
            if user_id is None:
                await qrws.send_error(
                    'Auth failed',
                    close_code=QrwsCloseCode.UNAUTHORIZED)
                return ws
            user = await repository.user_repository.get_by_id(user_id)

            await qrws.send_message(ServerReadyMessage())

            gateway = GatewayConnection(qrws, user)
            server.register_gateway(gateway)
            await gateway.handle_connection()
            return ws
        except QrwsCloseException as e:
            await ws.close(
                code=e.code,
                message=e.message.encode() if e.message else None)
            return ws
