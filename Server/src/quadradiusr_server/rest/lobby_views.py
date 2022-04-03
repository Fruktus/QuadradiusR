from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound

from quadradiusr_server.auth import Auth
from quadradiusr_server.db.base import Lobby
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.lobby import LobbyConnection
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import QrwsCloseException, QrwsConnection
from quadradiusr_server.rest.auth import authorized_endpoint, require_authorization
from quadradiusr_server.server import routes, QuadradiusRServer
from quadradiusr_server.utils import is_request_websocket_upgradable


def map_lobby_to_json(server: QuadradiusRServer, lobby: Lobby):
    return {
        'id': lobby.id_,
        'name': lobby.name_,
        'ws_url': server.get_href('ws') + f'/lobby/{lobby.id_}',
    }


@routes.view('/lobby')
class LobbiesView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        lobbies = await repository.lobby_repository.get_all()

        return web.json_response([map_lobby_to_json(server, l) for l in lobbies])


@routes.view('/lobby/{lobby_id}')
class LobbyView(web.View):
    @transactional
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        auth: Auth = self.request.app['auth']
        ns: NotificationService = self.request.app['notification']
        lobby = await self._get_lobby(repository)

        if not is_request_websocket_upgradable(self.request):
            await require_authorization(self.request)
            return web.json_response(map_lobby_to_json(server, lobby))

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        qrws = QrwsConnection(ws)
        user = await qrws.handshake(auth, repository)

        live_lobby = server.start_lobby(lobby)
        lobby_conn = LobbyConnection(live_lobby, qrws, user, ns)
        live_lobby.join(lobby_conn)
        try:
            await lobby_conn.handle_connection()
            return ws
        finally:
            live_lobby.leave(lobby_conn)

    async def _get_lobby(self, repository: Repository) -> Lobby:
        lobby_id = self.request.match_info.get('lobby_id')
        lobby = await repository.lobby_repository.get_by_id(lobby_id)
        if not lobby:
            raise HTTPNotFound()
        return lobby
