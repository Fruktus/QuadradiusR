from aiohttp import web

from quadradiusr_server.auth import User
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.rest.auth import authorized_endpoint

from quadradiusr_server.server import routes


@routes.view('/user')
class UsersView(web.View):
    @transactional
    async def post(self):
        return web.Response(status=501)
        # return web.Response(headers={
        #     'location': f'/user/{user.id_}'
        # })


@routes.view('/user/{user_id}')
class UserView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        user_id = self.request.match_info.get('user_id')
        if user_id != '@me' and user_id != auth_user.id_:
            return web.Response(status=403)

        return web.json_response({
            'id': auth_user.id_,
            'username': auth_user.username_,
        })
