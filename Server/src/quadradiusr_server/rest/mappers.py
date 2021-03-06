from typing import Optional, List

from quadradiusr_server.db.base import User, GameInvite, Game, LobbyMessage, Lobby
from quadradiusr_server.powers import PowerDefinition


def user_to_json(user: User):
    return {
        'id': user.id_,
        'username': user.username_,
    }


def game_invite_to_json(game_invite: GameInvite):
    return {
        'id': game_invite.id_,
        'from': user_to_json(game_invite.from_),
        'subject': user_to_json(game_invite.subject_),
        'expires_at': game_invite.expires_at_.isoformat(),
    }


def game_to_json(game: Game):
    return {
        'id': game.id_,
        'players': [
            user_to_json(game.player_a_),
            user_to_json(game.player_b_),
        ],
        'expires_at': game.expires_at_.isoformat(),
    }


def lobby_to_json(
        lobby: Lobby,
        *,
        href_ws: str,
        players: Optional[List[User]] = None):
    return {
        'id': lobby.id_,
        'name': lobby.name_,
        'ws_url': f'{href_ws}/lobby/{lobby.id_}/connect',
        'players': [
            user_to_json(player) for player in players
        ] if players is not None else None,
    }


def lobby_message_to_json(lobby_message: LobbyMessage):
    return {
        'id': lobby_message.id_,
        'lobby': {
            'id': lobby_message.lobby_id_,
        },
        'user': user_to_json(lobby_message.user_),
        'content': lobby_message.content_,
        'created_at': lobby_message.created_at_.isoformat(),
    }


def power_definition_to_json(power_definition: PowerDefinition):
    return {
        'id': power_definition.get_id(),
        'name': power_definition.get_name(),
        'description': power_definition.get_description(),
    }
