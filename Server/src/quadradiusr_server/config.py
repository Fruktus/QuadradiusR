from dataclasses import dataclass

import dacite as dacite
import toml as toml


@dataclass
class ServerConfig:
    host: str
    port: int


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
