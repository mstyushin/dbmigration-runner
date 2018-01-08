__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import os
import sys
import traceback
import time
from argparse import ArgumentParser
import util
import cli_commands
import logger


def main() -> int:
    """
    Main execution flow

    :return : 0 on success, 1 otherwise
    """
    # TODO: add meaningful description
    parser = ArgumentParser(description="""\r
        ***YOUR_HELP_MESSAGE_HERE***.\r
    """)
    parser.add_argument('--do',
                        dest='do',
                        choices=["%s" % action for action in util.get_available_actions()],
                        help='Specify action.',
                        required=True)
    parser.add_argument('--environment',
                        '-e',
                        dest='environment',
                        help='Specify environment. Default: dev',
                        default='dev')
    parser.add_argument('--project-dir',
                        '-d',
                        dest='project_dir',
                        help='Specify project directory.',
                        default='./')
    parser.add_argument('--migration-id',
                        '-m',
                        dest='migration_id',
                        help='Specify migration ID to work with.',
                        default=None)
    parser.add_argument('--log-level',
                        dest='log_level',
                        choices=["%s" % level for level in logger.Levels.__members__.keys()],
                        help='Specify logging level',
                        default='DEBUG')

    args = parser.parse_args()
    # TODO: I have no idea at this point about best practices of adding logging to python application
    app_logger = logger.Logger(level=logger.Levels[args.log_level])
    os_env = os.environ
    # TODO: will be great to have immutable config
    config = util.load_config(os.path.join(os.pardir, args.project_dir + '/pymigrate.conf'), app_logger)
    # Note that config dict should't have any values of None type
    config['MIGRATION_ID'] = str(args.migration_id) if args.migration_id else 'None'
    config['ENVIRONMENT'] = str(args.environment)
    config['PROJECT_DIR'] = os.path.abspath(args.project_dir)
    if 'MIGRATIONS_DIR' not in config:
        config['MIGRATIONS_DIR'] = args.project_dir + 'migrations'

    final_config = os_env.copy()
    final_config.update(config)

    # app_logger.log_plain('Starting with env:\n{0}'.format(util.get_formatted_env_vars()), logger.Levels.DEBUG)
    # app_logger.log_plain('Got config:\n{0}'.format(str(config)), logger.Levels.DEBUG)

    res = getattr(cli_commands, args.do)(final_config, app_logger)

    return 0 if res else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Got SIGINT, terminating')
        time.sleep(0.2)
        sys.exit(0)
    except Exception:
        print('Something went wrong, see traceback below')
        traceback.print_exc()
        sys.exit(1)
