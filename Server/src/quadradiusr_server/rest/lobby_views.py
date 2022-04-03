from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden

from quadradiusr_server.auth import Auth
from quadradiusr_server.db.base import Lobby, User, LobbyMessage
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional, transaction_context
from quadradiusr_server.lobby import LobbyConnection
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import QrwsConnection
from quadradiusr_server.rest.auth import authorized_endpoint, require_authorization
from quadradiusr_server.server import routes, QuadradiusRServer
from quadradiusr_server.utils import is_request_websocket_upgradable


def map_lobby_to_json(server: QuadradiusRServer, lobby: Lobby):
    return {
        'id': lobby.id_,
        'name': lobby.name_,
        'ws_url': server.get_href('ws') + f'/lobby/{lobby.id_}/connect',
    }


def map_lobby_message_to_json(lobby_message: LobbyMessage):
    return {
        'id': lobby_message.id_,
        'user': lobby_message.user_id_,
        'content': lobby_message.content_,
        'created_at': lobby_message.created_at_.isoformat(),
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
    @authorized_endpoint
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        lobby = await self._get_lobby(repository)
        return web.json_response(map_lobby_to_json(server, lobby))

    async def _get_lobby(self, repository: Repository) -> Lobby:
        lobby_id = self.request.match_info.get('lobby_id')
        lobby = await repository.lobby_repository.get_by_id(lobby_id)
        if not lobby:
            raise HTTPNotFound()
        return lobby


@routes.view('/lobby/{lobby_id}/connect')
class LobbyConnectView(web.View):
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        auth: Auth = self.request.app['auth']
        ns: NotificationService = self.request.app['notification']

        async with transaction_context(repository.database):
            lobby = await self._get_lobby(repository)
            qrws = QrwsConnection()
            await qrws.prepare(self.request)
            user = await qrws.authorize(auth, repository)

            await repository.expunge(lobby, user)

        live_lobby = server.start_lobby(lobby)
        lobby_conn = LobbyConnection(
            live_lobby, qrws, user,
            ns, repository.database)
        live_lobby.join(lobby_conn)
        try:
            await lobby_conn.handle_connection()
            return qrws.ws
        finally:
            live_lobby.leave(lobby_conn)

    async def _get_lobby(self, repository: Repository) -> Lobby:
        lobby_id = self.request.match_info.get('lobby_id')
        lobby = await repository.lobby_repository.get_by_id(lobby_id)
        if not lobby:
            raise HTTPNotFound()
        return lobby


@routes.view('/lobby/{lobby_id}/message')
class LobbyMessagesView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']

        lobby = await self._get_lobby(repository)
        live_lobby = server.start_lobby(lobby)

        if not live_lobby.joined(auth_user):
            raise HTTPForbidden()

        messages = await repository.lobby_repository.get_all_messages(lobby)
        return web.json_response([
            map_lobby_message_to_json(lm) for lm in messages])

    async def _get_lobby(self, repository: Repository) -> Lobby:
        lobby_id = self.request.match_info.get('lobby_id')
        lobby = await repository.lobby_repository.get_by_id(lobby_id)
        if not lobby:
            raise HTTPNotFound()
        return lobby
