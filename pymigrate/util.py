__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import sys
import os
import cli_commands
import logger
import fnmatch


def print_env_vars():
    """
    Print all environment variables available for current process.
    """
    print("Current process environment variables:")
    for k, v in os.environ.items():
        print('{0}={1}'.format(k, v))


def get_formatted_env_vars() -> str:
    """
    Return all environment variables available for current process.
    """
    res = ""
    for k, v in os.environ.items():
        res += '{0}={1}\n'.format(k, v)
    return res


def get_available_actions() -> tuple:
    """
    Return tuple with available actions.
    """
    return tuple(method for method in dir(cli_commands) if callable(getattr(cli_commands, method)))


def query_yes_no(question: str, default: str = "yes") -> bool:
    """
    Ask a yes/no question via input() and return user's answer.
    This function blocks until valid answer is given (or <Enter> is pressed).

    :param question: question string presented to user
    :param default: presumed answer if user just hits <Enter>. Must be "yes", "no" or None (meaning user answer is
    still pending)

    :return: True for "yes" or False for "no".
    """
    valid = {"yes": True,
             "y": True,
             "ye": True,
             "no": False,
             "n": False}

    if default is None:
        prompt = " [y/n]: "
    elif default == "yes":
        prompt = " [Y/n]: "
    elif default == "no":
        prompt = " [y/N]: "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no': ")


def load_config(config_file: str, app_logger: logger.Logger) -> dict:
    """
    Load properties from property file (if exists) into dict.

    :param config_file: path to property file.
    :param app_logger: instance of configured logger.

    :return: dict with loaded config (on success) or empty dict.
    """
    config = {}
    if os.path.isfile(config_file):
        app_logger.log_with_ts('Loading config file: {0}'.format(config_file), logger.Levels.DEBUG)
        with open(config_file, 'r') as cf:
            for line in cf:
                key, value = line.replace('\n', '').split('=')
                config[key] = value.replace("'", '')
            app_logger.log_with_ts('Loaded config file: {0}'.format(config_file), logger.Levels.DEBUG)
    else:
        app_logger.log_with_ts('Config file not found, moving on', logger.Levels.INFO)
    return config


def find_files(pattern: str, path: str, csensitive: bool) -> list:
    """
    Search for files by pattern. For case-insensitive search file names and pattern itself
    will be both normalized with str.lower().

    :param pattern: search regex.
    :param path: search under this path.
    :param csensitive: True for case-sensitive search, False otherwise.

    :return: list with all matches
    """
    def normalize(s: str):
        if csensitive:
            return s
        else:
            return s.lower()

    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(normalize(name), normalize(pattern)):
                result.append(os.path.join(root, name))
    return result


if __name__ == '__main__':
    print("This module is not callable")
    sys.exit(0)
