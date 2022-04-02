from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound

from quadradiusr_server.db.base import Lobby
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.server import routes


def map_lobby_to_json(lobby: Lobby):
    return {
        'id': lobby.id_,
        'name': lobby.name_,
    }


@routes.view('/lobby')
class LobbiesView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self):
        repository: Repository = self.request.app['repository']
        lobbies = await repository.lobby_repository.get_all()

        return web.json_response([map_lobby_to_json(l) for l in lobbies])


@routes.view('/lobby/{lobby_id}')
class LobbyView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self):
        repository: Repository = self.request.app['repository']
        lobby = await self._get_lobby(repository)

        return web.json_response(map_lobby_to_json(lobby))

    async def _get_lobby(self, repository: Repository) -> Lobby:
        lobby_id = self.request.match_info.get('lobby_id')
        lobby = await repository.lobby_repository.get_by_id(lobby_id)
        if not lobby:
            raise HTTPNotFound()
        return lobby
