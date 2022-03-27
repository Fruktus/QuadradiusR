from contextvars import ContextVar
from typing import Optional, Union, Callable

from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from quadradiusr_server.db.database_engine import DatabaseEngine
from quadradiusr_server.utils import filter_kwargs

_session_context: ContextVar[Optional[AsyncSession]] = \
    ContextVar('session_context', default=None)


def transactional(f):
    """
    This decorator is meant to be used on any method
    that should be transactional, i.e. a transaction is spanned on its code.

    In order to create a new session the annotated method must be a web.View.

    If the decorated method accepts kwarg ``db_session``,
    it is automatically populated with current database session.

    Currently, the only supported tx mode is REQUIRES.
    """

    async def wrapper(*args, **kwargs):
        async def call_transactional_method(s):
            kwargs['db_session'] = s
            return await f(*args, **filter_kwargs(f, kwargs))

        def obtain_db_engine() -> DatabaseEngine:
            if isinstance(args[0], web.View):
                view: web.View = args[0]
                database: DatabaseEngine = view.request.app['database']
                return database
            else:
                raise Exception('Failed to obtain a new database session')

        async with transaction_context(obtain_db_engine) as session:
            return await call_transactional_method(session)

    return wrapper


def transaction_context(
        database: Union[DatabaseEngine, Callable[[], DatabaseEngine]]):
    """
    Function meant to be used with ``async with`` statement.
    It introduces the transaction context, returning current
    database session.

    All code within the ``async with`` block will be executed
    in the context of this transaction.

    Currently, the only supported tx mode is REQUIRES.

    Examples:

    >>> async with transaction_context(database) as session:
    >>>    # use the session here

    >>> async with transaction_context(database):
    >>>    # call transactional methods
    """

    class TxContext(object):
        async def __aenter__(self):
            if _session_context.get() is not None:
                self.new_tx = False
                return _session_context.get()

            self.session = (database() if callable(database) else database).session()
            self.new_tx = True
            await self.session.__aenter__()
            self.token = _session_context.set(self.session)
            return self.session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if not self.new_tx:
                return
            if exc_type is None:
                await self.session.commit()
            _session_context.reset(self.token)
            await self.session.__aexit__(exc_type, exc_val, exc_tb)

    return TxContext()
