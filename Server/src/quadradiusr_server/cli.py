import argparse
import logging.config
import os.path

from quadradiusr_server import config
from quadradiusr_server.config import ConfigGenerator
from quadradiusr_server.server import QuadradiusRServer


class ServerCli:
    def __init__(self, args) -> None:
        self.args = self._parse_args(args)

    @staticmethod
    def _parse_args(args):
        parser = argparse.ArgumentParser(description='The official QuadradiusR server.')
        parser.add_argument(
            '--config',
            type=str,
            default='config.toml',
            help='specify path of the configuration file')
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='enable verbose output')
        parser.add_argument(
            '--generate-config',
            metavar='CONFIG_PATH',
            help='generate server configuration')

        return parser.parse_args(args)

    def run(self) -> int:
        args = self.args
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'standard': {
                    'class': 'logging.Formatter',
                    'format': '[{asctime}.{msecs:3.0f}] {levelname} {message}',
                    'style': '{',
                    'datefmt': '%H:%M:%S',
                },
                'verbose': {
                    'class': 'logging.Formatter',
                    'format': '{asctime} {threadName:10} [{name:24}] {levelname:7} {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'default': {
                    'class': 'logging.StreamHandler',
                    'level': 'DEBUG' if args.verbose else 'INFO',
                    'formatter': 'verbose' if args.verbose else 'standard',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['default'],
                    'level': 'DEBUG',
                },
            },
        })

        if args.generate_config:
            gen = ConfigGenerator()
            gen.generate(args.generate_config)
            return 0

        if not os.path.isfile(args.config):
            logging.error(f'Config file {args.config} not found')
            return 1

        server = QuadradiusRServer(config.from_toml(args.config))
        return server.run()
