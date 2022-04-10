import dataclasses
import json
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import Optional, Callable

import dacite as dacite
import toml as toml


@dataclass
class AuthConfig:
    token_exp: int = 60
    token_leeway: int = 10
    scrypt_n: int = 16 * 1024
    scrypt_r: int = 8
    scrypt_p: int = 1


@dataclass
class DatabaseConfig:
    url: str = 'sqlite+aiosqlite://'
    create_metadata: bool = False
    log_statements: bool = False
    log_connections: bool = False
    hide_parameters: bool = True
    pool_recycle_timeout: int = -1


@dataclass
class CronConfig:
    purge_game_invites_delay: float = 10


@dataclass
class StaticServerConfig:
    serve_path: Optional[str] = None
    redirect_root: Optional[str] = None


@dataclass
class ServerConfig:
    host: str
    port: int

    href: Optional[str] = None
    reuse_port: Optional[bool] = None
    reuse_address: Optional[bool] = None
    shutdown_timeout: float = 60.0
    backlog: int = 128

    auth: AuthConfig = field(default_factory=AuthConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cron: CronConfig = field(default_factory=CronConfig)
    static: StaticServerConfig = field(default_factory=StaticServerConfig)

    def set(self, option: str, value: str):
        option_parts = option.split('.')
        if option_parts[0] == 'server':
            option_parts = option_parts[1:]
        obj = self
        for part in option_parts[0:-1]:
            obj = getattr(obj, part)
        attr = option_parts[-1]
        if not hasattr(obj, attr):
            raise KeyError(f'Unknown option: {option}')

        try:
            setattr(obj, attr, json.loads(value))
        except JSONDecodeError:
            setattr(obj, attr, value)


class ConfigError(Exception):
    pass


def from_toml(path) -> ServerConfig:
    @dataclass
    class Config:
        server: ServerConfig

    try:
        data = toml.load(path)
        return dacite.from_dict(
            data_class=Config,
            data=dict(data),
            config=dacite.config.Config(strict=True),
        ).server
    except Exception as e:
        raise ConfigError(f'Error while loading configuration {path}') from e


def to_toml(server_config: ServerConfig, path):
    try:
        with open(path, 'x') as f:
            toml.dump({
                'server': dataclasses.asdict(server_config),
            }, f)
    except Exception as e:
        raise ConfigError(f'Error while saving configuration {path}') from e


class ConfigGenerator:

    def _ask(
            self, *,
            question: str, default,
            mapper: Callable[[str], any] = None):
        while True:
            answer = input(f'{question}\n[{default}] > ')
            if answer == '':
                return default
            if mapper:
                try:
                    return mapper(answer)
                except (ValueError, KeyError):
                    print('Invalid format')
                    continue
            else:
                return answer

    def generate(self, destination: str):
        config = ServerConfig(host='0.0.0.0', port=8080)
        config.host = self._ask(
            question='[server.host] Bind address',
            default='0.0.0.0',
        )
        config.port = self._ask(
            question='[server.port] Bind port',
            default=8080,
            mapper=int,
        )
        config.href = self._ask(
            question='[server.href] Address used for self-referencing',
            default=config.href,
        )
        config.shutdown_timeout = self._ask(
            question='[server.shutdown_timeout] Server shutdown timeout in seconds',
            default=config.shutdown_timeout,
            mapper=float,
        )
        config.backlog = self._ask(
            question='[server.backlog] Number of unaccepted connections that '
                     'the system will allow before refusing new connections',
            default=config.backlog,
            mapper=int,
        )
        config.database.url = self._ask(
            question='[server.database.url] Database URL',
            default=config.database.url,
        )
        config.database.create_metadata = self._ask(
            question='[server.database.create_metadata] Create database metadata on startup',
            default=config.database.create_metadata,
            mapper=bool,
        )
        to_toml(config, destination)
