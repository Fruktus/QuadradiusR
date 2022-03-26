from dataclasses import dataclass
from typing import Optional

import dacite as dacite
import toml as toml


@dataclass
class AuthConfig:
    token_exp: int = 60
    token_leeway: int = 10


@dataclass
class DatabaseConfig:
    url: str = 'sqlite+aiosqlite://'
    create_metadata: bool = False
    log_statements: bool = False
    log_connections: bool = False
    hide_parameters: bool = True
    pool_recycle_timeout: int = -1


@dataclass
class ServerConfig:
    host: str
    port: int

    href: Optional[str] = None
    reuse_port: Optional[bool] = None
    reuse_address: Optional[bool] = None
    shutdown_timeout: float = 60.0
    backlog: int = 128

    auth: AuthConfig = AuthConfig()
    database: DatabaseConfig = DatabaseConfig()


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
