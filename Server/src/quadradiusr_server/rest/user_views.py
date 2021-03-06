import logging
import uuid
from json import JSONDecodeError

from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict

from quadradiusr_server.auth import User, Auth
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.rest.mappers import user_to_json
from quadradiusr_server.server import routes


@routes.view('/user')
class UsersView(web.View):
    @transactional
    async def post(self):
        repository: Repository = self.request.app['repository']
        auth: Auth = self.request.app['auth']

        try:
            body = await self.request.json()
            username = str(body['username'])
            password = str(body['password'])
        except (JSONDecodeError, KeyError):
            raise HTTPBadRequest(reason='Malformed request body')

        existing_user = await repository.user_repository.get_by_username(username)
        if existing_user is not None:
            raise HTTPConflict(reason='User already exists')

        user = User(
            id_=str(uuid.uuid4()),
            username_=username,
            password_=auth.hash_password(password.encode('utf-8')),
        )
        await repository.user_repository.add(user)
        logging.info(f'New user created: {user.friendly_name}')

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

        json = user_to_json(auth_user)
        return web.json_response(json)
