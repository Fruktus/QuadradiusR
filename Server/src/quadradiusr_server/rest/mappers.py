from quadradiusr_server.db.base import User, GameInvite, Game


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
