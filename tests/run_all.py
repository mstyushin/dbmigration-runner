import test_util

__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import unittest


def main() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    # TODO: Add moar tests! and try to use TDD approach
    suite.addTest(test_util.TestUtilModule('test_get_formatted_env_vars'))
    suite.addTest(test_util.TestUtilModule('test_load_config_return_dict'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(main())
