from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden, HTTPConflict

from quadradiusr_server.auth import User, Auth
from quadradiusr_server.db.base import GameInvite
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.game import GameConnection
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import QrwsConnection, QrwsCloseException
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.server import routes, QuadradiusRServer
from quadradiusr_server.utils import is_request_websocket_upgradable


@routes.view('/game/{game_id}')
class GameView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        server: QuadradiusRServer = self.request.app['server']
        auth: Auth = self.request.app['auth']
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']
        game = await self._get_game(auth_user, repository)

        if not is_request_websocket_upgradable(self.request):
            return web.json_response({
                'id': game.id_,
                'players': [
                    game.player_a_id_,
                    game.player_b_id_,
                ],
                'expiration': game.expiration_.isoformat(),
                'ws_url': server.get_href('ws') + f'/game/{game.id_}',
            })

        game_in_progress = server.start_game(game)
        if game_in_progress.is_player_connected(auth_user.id_):
            raise HTTPConflict()

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        qrws = QrwsConnection(ws)
        user = await qrws.handshake(auth, repository)

        conn = GameConnection(qrws, user, ns)
        game_in_progress.connect_player(conn)
        try:
            await conn.handle_connection()
            return ws
        finally:
            game_in_progress.disconnect_player(conn)

    async def _get_game(
            self, auth_user: User,
            repository: Repository) -> GameInvite:
        game_id = self.request.match_info.get('game_id')
        game = await repository.game_repository.get_by_id(game_id)
        if not game:
            raise HTTPNotFound()
        if auth_user.id_ != game.player_a_id_ and \
                auth_user.id_ != game.player_b_id_:
            raise HTTPForbidden()
        return game
