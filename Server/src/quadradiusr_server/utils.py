import importlib
import inspect
import pkgutil
from inspect import Parameter

from aiohttp.abc import Request
from isodate import parse_datetime


def import_submodules(package, recursive=True):
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def can_pass_argument(f, name: str):
    f_signature = inspect.signature(f)
    for param in f_signature.parameters.values():
        if param.kind == Parameter.VAR_KEYWORD:
            # **kwargs
            return True
        is_keyword = (
                param.kind == Parameter.KEYWORD_ONLY or
                param.kind == Parameter.POSITIONAL_OR_KEYWORD)
        if is_keyword and param.name == name:
            return True
    return False


def filter_kwargs(f, kwargs):
    kwargs = dict(kwargs)
    kws = list(kwargs.keys())
    for name in kws:
        if not can_pass_argument(f, name):
            del kwargs[name]
    return kwargs


def is_request_websocket_upgradable(request: Request):
    return 'connection' in request.headers and \
           'upgrade' == request.headers['connection'].lower() and \
           'upgrade' in request.headers and \
           'websocket' == request.headers['upgrade'].lower()


def parse_iso_datetime_tz(string: str):
    dt = parse_datetime(string)
    if dt.tzinfo is None:
        raise ValueError('datetime lacks timezone')
    return dt
