from abc import ABCMeta
from datetime import datetime, timezone

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden, HTTPBadRequest

from quadradiusr_server.auth import Auth
from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Lobby, User
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional, transaction_context
from quadradiusr_server.lobby import LobbyConnection
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import QrwsConnection
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.rest.mappers import lobby_message_to_json, lobby_to_json
from quadradiusr_server.server import routes, QuadradiusRServer
from quadradiusr_server.utils import parse_iso_datetime_tz


class LobbyViewBase(web.View, metaclass=ABCMeta):
    async def _get_lobby(self, repository: Repository) -> Lobby:
        lobby_id = self.request.match_info.get('lobby_id')
        lobby = await repository.lobby_repository.get_by_id(lobby_id)
        if not lobby:
            raise HTTPNotFound(reason='Lobby not found')
        return lobby


@routes.view('/lobby')
class LobbiesView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        lobbies = await repository.lobby_repository.get_all()

        return web.json_response([lobby_to_json(
            lobby,
            href_ws=server.get_href('ws'),
        ) for lobby in lobbies])


@routes.view('/lobby/{lobby_id}')
class LobbyView(LobbyViewBase, web.View):
    @transactional
    @authorized_endpoint
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        lobby = await self._get_lobby(repository)
        live_lobby = server.start_lobby(lobby)
        players = await live_lobby.get_players()
        return web.json_response(lobby_to_json(
            lobby,
            href_ws=server.get_href('ws'),
            players=players,
        ))


@routes.view('/lobby/{lobby_id}/connect')
class LobbyConnectView(LobbyViewBase, web.View):
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        auth: Auth = self.request.app['auth']
        ns: NotificationService = self.request.app['notification']

        if 'force' in self.request.rel_url.query:
            force = bool(self.request.rel_url.query['force'])
        else:
            force = False

        async with transaction_context(repository.database):
            lobby = await self._get_lobby(repository)
            qrws = QrwsConnection()
            await qrws.prepare(self.request)
            user = await qrws.authorize(auth, repository)

            live_lobby = server.start_lobby(lobby)
            if live_lobby.joined(user) and not force:
                await qrws.send_error(
                    'You are already connected to this lobby',
                    close_code=QrwsCloseCode.CONFLICT)
                return qrws.ws

            lobby_conn = LobbyConnection(
                live_lobby, qrws, user,
                ns, repository)
            await live_lobby.join(lobby_conn)

        try:
            await lobby_conn.handle_connection()
            return qrws.ws
        finally:
            await live_lobby.leave(lobby_conn)


@routes.view('/lobby/{lobby_id}/message')
class LobbyMessagesView(LobbyViewBase, web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']

        lobby = await self._get_lobby(repository)
        live_lobby = server.start_lobby(lobby)

        if not live_lobby.joined(auth_user):
            raise HTTPForbidden(reason='User not inside the lobby')

        try:
            if 'before' in self.request.rel_url.query:
                before_str = str(self.request.rel_url.query['before'])
                before = parse_iso_datetime_tz(before_str)
            else:
                before = datetime.now(timezone.utc)

            if 'limit' in self.request.rel_url.query:
                limit = int(self.request.rel_url.query['limit'])
            else:
                limit = 100
        except (ValueError, AssertionError):
            raise HTTPBadRequest(reason='Malformed query params')

        if limit > 100:
            raise HTTPBadRequest(reason='Limit too high')

        messages = await repository.lobby_repository.get_messages(
            lobby.id_,
            before=before,
            limit=limit,
        )
        return web.json_response([
            lobby_message_to_json(lm) for lm in messages])
