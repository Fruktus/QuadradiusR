import argparse
import logging.config
import os.path

from quadradiusr_server import config, logger
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
            action='count', default=0,
            help='enable verbose output (it stacks)')
        parser.add_argument(
            '--generate-config',
            metavar='CONFIG_PATH',
            help='generate server configuration')

        return parser.parse_args(args)

    def run(self) -> int:
        args = self.args
        logger.configure_logger(args.verbose)

        if args.generate_config:
            gen = ConfigGenerator()
            gen.generate(args.generate_config)
            return 0

        if not os.path.isfile(args.config):
            logging.error(f'Config file {args.config} not found')
            return 1

        server = QuadradiusRServer(config.from_toml(args.config))
        return server.run()
