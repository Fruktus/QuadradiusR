from dataclasses import dataclass
from typing import Optional

import dacite as dacite
import toml as toml


@dataclass
class ServerConfig:
    host: str
    port: int

    reuse_port: Optional[bool] = None
    reuse_address: Optional[bool] = None
    shutdown_timeout: float = 60.0
    backlog: int = 128


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
            data=dict(data)).server
    except Exception as e:
        raise ConfigError(f'Error while loading configuration {path}') from e
