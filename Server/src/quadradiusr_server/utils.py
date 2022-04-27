import importlib
import inspect
import pkgutil
from inspect import Parameter
from typing import Optional, Type

from aiohttp.abc import Request
from isodate import parse_datetime
from jsondiff import CompactJsonDiffSyntax, symbols


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


def import_class(full_name: str, *, subtype_of: Type = None) -> Type:
    if '.' not in full_name:
        raise ValueError(f'Class {full_name} cannot be imported because there is no module')
    module_name, class_name = full_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    clazz = getattr(module, class_name)
    if subtype_of and not issubclass(clazz, subtype_of):
        raise ValueError(f'{clazz} should be a subclass of {subtype_of}')
    return clazz


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


def parse_etag_header(header_value):
    if header_value[0] != '"' or header_value[-1] != '"':
        return None
    return header_value[1:-1]


def get_if_none_match_from_request(request: Request) -> Optional[str]:
    if 'if-none-match' in request.headers:
        return parse_etag_header(request.headers['if-none-match'])
    return None


def parse_iso_datetime_tz(string: str):
    dt = parse_datetime(string)
    if dt.tzinfo is None:
        raise ValueError('datetime lacks timezone')
    return dt


class SimpleJsonDiffSyntax(CompactJsonDiffSyntax):
    def emit_dict_diff(self, a, b, s, added, changed, removed):
        if s == 1.0:
            return {}
        else:
            changed.update(added)
            if removed:
                changed[symbols.delete] = list(removed.keys())
            return changed
