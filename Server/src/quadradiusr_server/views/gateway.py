from aiohttp import web

from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.gateway import GatewayConnection
from quadradiusr_server.qrws_connection import QrwsConnection, QrwsCloseException
from quadradiusr_server.qrws_messages import IdentifyMessage, ServerReadyMessage
from quadradiusr_server.server import routes, QuadradiusRServer


@routes.view('/gateway')
class GatewayView(web.View):
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']

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

            user = server.auth.authenticate(identify_msg.token)
            if user is None:
                await qrws.send_error(
                    'Auth failed',
                    close_code=QrwsCloseCode.UNAUTHORIZED)
                return ws

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
