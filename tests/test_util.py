import unittest

import os
__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import util
import logger
import sys


class TestUtilModule(unittest.TestCase):
    test_config_file_path = '/tmp/test_config'

    def setUp(self):
        os.environ['TEST_VAR'] = 'TEST_VALUE'
        with open(os.path.abspath('/tmp/test_config'), 'w') as test_config_file:
            test_config_file.write('SOME_CONFIG_VAR=SOME_CONFIG_VALUE\n')

    def tearDown(self):
        os.remove('/tmp/test_config')

    def test_get_formatted_env_vars(self):
        env_vars_string = util.get_formatted_env_vars()
        self.assertTrue('TEST_VAR=TEST_VALUE' in env_vars_string, 'Test variable was not read')

    def test_load_config_return_dict(self):
        d = util.load_config('/tmp/test_config', logger.Logger(level=logger.Levels.ERROR))
        self.assertIsInstance(d, dict)


if __name__ == '__main__':
    print("This module is not callable")
    sys.exit(0)
