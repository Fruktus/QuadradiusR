import argparse
import logging.config
import os.path

from quadradiusr_server import config, logger
from quadradiusr_server.config import ConfigGenerator, ServerConfig
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
            help='specify path of the configuration file')
        parser.add_argument(
            '-v', '--verbose',
            action='count', default=0,
            help='enable verbose output (it stacks)')
        parser.add_argument(
            '--generate-config',
            metavar='CONFIG_PATH',
            help='generate server configuration')
        parser.add_argument(
            '--q',
            type=bool,
            help='use default configuration instead of ')
        parser.add_argument(
            '--host',
            type=str,
            help='bind address')
        parser.add_argument(
            '--port',
            type=str,
            help='bind port')
        parser.add_argument(
            '--set',
            action='append',
            help='set config values, e.g. --set server.database.create_metadata=true')

        return parser.parse_args(args)

    def run(self) -> int:
        args = self.args
        logger.configure_logger(args.verbose)

        if args.generate_config:
            gen = ConfigGenerator()
            gen.generate(args.generate_config)
            return 0

        if args.config:
            if not os.path.isfile(args.config):
                logging.error(f'Config file {args.config} not found')
                return 1

            server_config = config.from_toml(args.config)
        else:
            if not args.host or not args.port:
                logging.error('No --host, --port, or --config option, see --help for help')
                return 1

            server_config = ServerConfig(
                host=args.host,
                port=int(args.port),
            )

        set_options = args.set
        if set_options:
            for set_option in set_options:
                set_option: str
                option, value = set_option.split('=', 2)
                server_config.set(option, value)

        server = QuadradiusRServer(server_config)
        return server.run()
