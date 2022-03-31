import uuid
from json import JSONDecodeError

from aiohttp import web

from quadradiusr_server.auth import User, hash_password
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.server import routes


@routes.view('/user')
class UsersView(web.View):
    @transactional
    async def post(self):
        repository: Repository = self.request.app['repository']

        try:
            body = await self.request.json()
            username = str(body['username'])
            password = str(body['password'])
        except (JSONDecodeError, KeyError):
            return web.Response(status=400)

        existing_user = await repository.user_repository.get_by_username(username)
        if existing_user is not None:
            return web.Response(status=400)

        user = User(
            id_=str(uuid.uuid4()),
            username_=username,
            password_=hash_password(password.encode('utf-8')),
        )
        await repository.user_repository.add(user)

        return web.Response(status=201, headers={
            'location': f'/user/{user.id_}',
        })


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
