from quadradiusr_server.db.base import User


def user_to_json(user: User):
    return {
        'id': user.id_,
        'username': user.username_,
    }
