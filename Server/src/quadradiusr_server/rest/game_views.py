from abc import ABCMeta

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden, HTTPConflict

from quadradiusr_server.auth import User, Auth
from quadradiusr_server.db.base import GameInvite
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.game import GameConnection
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import QrwsConnection
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.server import routes, QuadradiusRServer


class GameViewBase(web.View, metaclass=ABCMeta):
    async def _get_game(
            self, auth_user: User,
            repository: Repository) -> GameInvite:
        game_id = self.request.match_info.get('game_id')
        game = await repository.game_repository.get_by_id(game_id)
        if not game:
            raise HTTPNotFound(reason='Game not found')
        if auth_user.id_ != game.player_a_id_ and \
                auth_user.id_ != game.player_b_id_:
            raise HTTPForbidden(reason='You are not a part of this game, sorry')
        return game


@routes.view('/game/{game_id}')
class GameView(GameViewBase, web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        server: QuadradiusRServer = self.request.app['server']
        repository: Repository = self.request.app['repository']
        game = await self._get_game(auth_user, repository)

        return web.json_response({
            'id': game.id_,
            'players': [
                {
                    'id': game.player_a_id_,
                },
                {
                    'id': game.player_b_id_,
                },
            ],
            'expiration': game.expiration_.isoformat(),
            'ws_url': server.get_href('ws') + f'/game/{game.id_}/connect',
        })


@routes.view('/game/{game_id}/connect')
class GameConnectView(GameViewBase, web.View):
    async def get(self, *, auth_user: User):
        server: QuadradiusRServer = self.request.app['server']
        auth: Auth = self.request.app['auth']
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']
        game = await self._get_game(auth_user, repository)

        game_in_progress = server.start_game(game)
        if game_in_progress.is_player_connected(auth_user.id_):
            raise HTTPConflict(reason='You are already connected to this game')

        qrws = QrwsConnection()
        await qrws.prepare(self.request)
        user = await qrws.authorize(auth, repository)

        conn = GameConnection(qrws, user, ns, repository.database)
        game_in_progress.connect_player(conn)
        try:
            await conn.handle_connection()
            return qrws.ws
        finally:
            game_in_progress.disconnect_player(conn)
