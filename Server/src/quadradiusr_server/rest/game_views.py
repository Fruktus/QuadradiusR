from abc import ABCMeta

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden

from quadradiusr_server.auth import User, Auth
from quadradiusr_server.constants import QrwsCloseCode
from quadradiusr_server.db.base import Game
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional, transaction_context
from quadradiusr_server.game import GameConnection, GameState
from quadradiusr_server.notification import NotificationService
from quadradiusr_server.qrws_connection import QrwsConnection
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.rest.mappers import game_to_json
from quadradiusr_server.server import routes, QuadradiusRServer
from quadradiusr_server.utils import get_if_none_match_from_request


class GameViewBase(web.View, metaclass=ABCMeta):
    async def _get_game(
            self, auth_user: User,
            repository: Repository) -> Game:
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
            **game_to_json(game),
            'ws_url': server.get_href('ws') + f'/game/{game.id_}/connect',
        })


@routes.view('/game/{game_id}/connect')
class GameConnectView(GameViewBase, web.View):
    async def get(self):
        server: QuadradiusRServer = self.request.app['server']
        auth: Auth = self.request.app['auth']
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']

        if 'force' in self.request.rel_url.query:
            force = bool(self.request.rel_url.query['force'])
        else:
            force = False

        async with transaction_context(repository.database):
            qrws = QrwsConnection()
            await qrws.prepare(self.request)
            user = await qrws.authorize(auth, repository)
            game = await self._get_game(user, repository)

            await repository.expunge_all()

        game_in_progress = server.start_game(game)
        if game_in_progress.is_player_connected(user.id_) and not force:
            await qrws.send_error(
                'You are already connected to this game',
                close_code=QrwsCloseCode.CONFLICT)
            return qrws.ws

        conn = GameConnection(qrws, game_in_progress, user, ns, repository.database)
        await game_in_progress.connect_player(conn)
        try:
            await conn.handle_connection()
            return qrws.ws
        finally:
            await game_in_progress.disconnect_player(conn)


@routes.view('/game/{game_id}/state')
class GameStateView(GameViewBase, web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        game = await self._get_game(auth_user, repository)
        game_state: GameState = game.game_state_
        serialized, etag = game_state.serialize_with_etag_for(auth_user)

        user_etag = get_if_none_match_from_request(self.request)
        if user_etag and etag == user_etag:
            return web.Response(status=304)

        return web.json_response({
            'game_id': game.id_,
            **serialized,
        }, headers={
            'etag': f'"{etag}"',
        })
