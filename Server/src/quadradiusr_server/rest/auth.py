from aiohttp import web
from aiohttp.web_exceptions import HTTPUnauthorized

from quadradiusr_server.db.base import User
from quadradiusr_server.utils import filter_kwargs


async def require_authorization(request) -> User:
    server = request.app['server']
    token = request.headers.get('authorization') \
        if 'authorization' in request.headers else None

    user_id = server.auth.authenticate(token)
    if not user_id:
        raise HTTPUnauthorized()
    user = await server.repository.user_repository.get_by_id(user_id)
    if not user:
        raise HTTPUnauthorized()
    return user


def authorized_endpoint(f):
    """
    This decorator is meant to be used on a method of a web.View.
    It requires proper authorization on this specific endpoint returning
    401 if not provided or invalid.

    If the decorated method accepts kwargs ``auth_user_id`` or ``auth_user``
    it is automatically populated respectively with
    the authorized user's ID, and its object.
    """

    async def wrapper(*args, **kwargs):
        view = args[0]
        assert isinstance(view, web.View)

        request = view.request
        user = await require_authorization(request)

        kwargs['auth_user_id'] = user.id_
        kwargs['auth_user'] = user

        return await f(*args, **filter_kwargs(f, kwargs))

    return wrapper
