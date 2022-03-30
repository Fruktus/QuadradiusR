from json import JSONDecodeError

from aiohttp import web

from quadradiusr_server.auth import Auth
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.server import routes


@routes.view('/authorize')
class AuthorizeView(web.View):
    @transactional
    async def post(self):
        auth: Auth = self.request.app['auth']

        try:
            body = await self.request.json()
            username = str(body['username'])
            password = str(body['password'])
        except JSONDecodeError | KeyError:
            return web.Response(status=400)

        user = await auth.login(
            username=username,
            password=password.encode('utf-8'))
        if user is None:
            return web.Response(status=401)

        token = auth.issue_token(user)
        return web.json_response({
            'token': token,
        })
