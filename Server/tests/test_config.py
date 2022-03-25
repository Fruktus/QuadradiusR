import glob
import logging
from unittest import TestCase

from quadradiusr_server.config import from_toml, ConfigError


class Test(TestCase):
    def test_from_toml(self):
        should_pass = glob.glob('test_config/*_pass.toml')
        should_fail = glob.glob('test_config/*_fail.toml')

        for path in should_pass:
            logging.info(f'Checking {path}')
            config = from_toml(path)
            self.assertIsNotNone(config)

        for path in should_fail:
            logging.info(f'Checking {path}')
            self.assertRaises(ConfigError, lambda: from_toml(path))
