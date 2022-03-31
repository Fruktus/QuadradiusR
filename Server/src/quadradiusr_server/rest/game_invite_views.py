import datetime
import uuid
from json import JSONDecodeError

import dateutil.parser
from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden, HTTPBadRequest, HTTPNotImplemented

from quadradiusr_server.auth import User
from quadradiusr_server.db.base import GameInvite
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.notification import Notification, NotificationService
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.server import routes


@routes.view('/game_invite')
class GameInvitesView(web.View):
    @transactional
    @authorized_endpoint
    async def post(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']

        try:
            body = await self.request.json()
            subject_id = str(body['subject'])
            expiration = dateutil.parser.isoparse(str(body['expiration']))
        except (JSONDecodeError, KeyError, ValueError):
            raise HTTPBadRequest()

        if subject_id == auth_user.id_:
            raise HTTPBadRequest()
        if expiration < datetime.datetime.now():
            raise HTTPBadRequest()
        if expiration > datetime.datetime.now() + \
                datetime.timedelta(minutes=60):
            raise HTTPBadRequest()

        subject = await repository.user_repository.get_by_id(subject_id)
        if subject is None:
            raise HTTPBadRequest()

        game_invite = GameInvite(
            id_=str(uuid.uuid4()),
            from_id_=auth_user.id_,
            subject_id_=subject_id,
            expiration_=expiration,
        )
        await repository.game_invite_repository.add(game_invite)

        ns.notify(Notification(
            topic='game.invite.received',
            subject_id=subject_id,
            data={
                'game_invite_id': game_invite.id_,
            },
        ))

        return web.Response(status=201, headers={
            'location': f'/game_invite/{game_invite.id_}',
        })


@routes.view('/game_invite/{game_invite_id}')
class GameInviteView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        game_invite = await self._get_game_invite(auth_user, repository)

        return web.json_response({
            'id': game_invite.id_,
            'from': game_invite.from_id_,
            'subject': game_invite.subject_id_,
            'expiration': game_invite.expiration_.isoformat(),
        })

    @transactional
    @authorized_endpoint
    async def delete(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        game_invite = await self._get_game_invite(auth_user, repository)
        await repository.game_invite_repository.remove(game_invite)
        return web.Response(status=204)

    async def _get_game_invite(
            self, auth_user: User, repository: Repository) -> GameInvite:
        game_invite_id = self.request.match_info.get('game_invite_id')
        game_invite = await repository.game_invite_repository.get_by_id(game_invite_id)
        if not game_invite:
            raise HTTPNotFound()
        if auth_user.id_ != game_invite.from_id_ and \
                auth_user.id_ != game_invite.subject_id_:
            raise HTTPForbidden()
        return game_invite


@routes.view('/game_invite/{game_invite_id}/accept')
class GameInviteAcceptView(web.View):
    @transactional
    @authorized_endpoint
    async def post(self, *, auth_user: User):
        raise HTTPNotImplemented()
