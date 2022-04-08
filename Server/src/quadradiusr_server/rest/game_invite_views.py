import datetime
import uuid
from abc import ABCMeta
from json import JSONDecodeError

import isodate as isodate
from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound, HTTPForbidden, HTTPBadRequest

from quadradiusr_server.auth import User
from quadradiusr_server.db.base import GameInvite, Game
from quadradiusr_server.db.repository import Repository
from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.game import GameState
from quadradiusr_server.notification import Notification, NotificationService
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.rest.mappers import game_invite_to_json, game_to_json
from quadradiusr_server.server import routes


class GameInviteViewBase(web.View, metaclass=ABCMeta):
    async def _get_game_invite(
            self, auth_user: User, repository: Repository) -> GameInvite:
        game_invite_id = self.request.match_info.get('game_invite_id')
        game_invite = await repository.game_invite_repository.get_by_id(game_invite_id)
        if not game_invite:
            raise HTTPNotFound(reason='Game invite not found')
        if auth_user.id_ != game_invite.from_id_ and \
                auth_user.id_ != game_invite.subject_id_:
            raise HTTPForbidden(reason='You are not a part of the invite')
        return game_invite


@routes.view('/game_invite')
class GameInvitesView(web.View):
    @transactional
    @authorized_endpoint
    async def post(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']

        try:
            body = await self.request.json()
            subject_id = str(body['subject_id'])
            expires_in = isodate.parse_duration(str(body.get('expires_in', 'PT2M')))
        except (JSONDecodeError, KeyError, ValueError):
            raise HTTPBadRequest(reason='Malformed body data')

        if subject_id == auth_user.id_:
            raise HTTPBadRequest(reason='User cannot invite themselves... or can they?')
        if expires_in < datetime.timedelta():
            raise HTTPBadRequest(reason='Invite cannot expire in the past')
        if expires_in > datetime.timedelta(minutes=60):
            raise HTTPBadRequest(reason='Expiration date too late')

        subject = await repository.user_repository.get_by_id(subject_id)
        if subject is None:
            raise HTTPBadRequest(reason='Subject not found')

        game_invite = GameInvite(
            id_=str(uuid.uuid4()),
            expires_at_=datetime.datetime.now(datetime.timezone.utc) + expires_in,
            from_=auth_user,
            subject_=subject,
        )
        await repository.game_invite_repository.add(game_invite)

        ns.notify(Notification(
            topic='game.invite.received',
            subject_id=subject_id,
            data={
                'game_invite': game_invite_to_json(game_invite),
            },
        ))

        return web.Response(status=201, headers={
            'location': f'/game_invite/{game_invite.id_}',
        })


@routes.view('/game_invite/{game_invite_id}')
class GameInviteView(GameInviteViewBase, web.View):
    @transactional
    @authorized_endpoint
    async def get(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        game_invite = await self._get_game_invite(auth_user, repository)

        return web.json_response(game_invite_to_json(game_invite))

    @transactional
    @authorized_endpoint
    async def delete(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']

        game_invite = await self._get_game_invite(auth_user, repository)
        await repository.game_invite_repository.remove(game_invite)

        ns.notify(Notification(
            topic='game.invite.removed',
            subject_id=game_invite.get_other_player(auth_user).id_,
            data={
                'game_invite_id': game_invite.id_,
                'reason': 'canceled',
            },
        ))

        return web.Response(status=204)


@routes.view('/game_invite/{game_invite_id}/accept')
class GameInviteAcceptView(GameInviteViewBase, web.View):
    @transactional
    @authorized_endpoint
    async def post(self, *, auth_user: User):
        repository: Repository = self.request.app['repository']
        ns: NotificationService = self.request.app['notification']

        game_invite = await self._get_game_invite(auth_user, repository)
        if auth_user.id_ != game_invite.subject_id_:
            raise HTTPForbidden(reason='You are not the person being invited')

        game = Game(
            id_=str(uuid.uuid4()),
            player_a_=game_invite.from_,
            player_b_=game_invite.subject_,
            expires_at_=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5),
            game_state_=GameState.initial()
        )

        await repository.game_repository.add(game)
        await repository.game_invite_repository.remove(game_invite)

        ns.notify(Notification(
            topic='game.invite.accepted',
            subject_id=game_invite.get_other_player(auth_user).id_,
            data={
                'game_invite_id': game_invite.id_,
                'game': game_to_json(game),
            },
        ))

        return web.Response(status=303, headers={
            'location': f'/game/{game.id_}',
        })
