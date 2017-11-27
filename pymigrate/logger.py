__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import datetime
import sys
from enum import IntEnum


class Levels(IntEnum):
    """
    Enum representing log levels in application. Greater value means greater verbosity.
    """
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


class Logger:
    """
    Logger class is responsible for logging messages to specified TextIOWrapper object.
    Each message is tagged by some log level from Level enum.
    """

    def __init__(self, path_to_log: str = None, level: Levels = Levels.INFO):
        self.path_to_log = path_to_log
        self.level = level

    def __repr__(self):
        return '[ {0}: {1}, {2}: {3} ]'.format('path_to_log',
                                               self.path_to_log,
                                               'level',
                                               self.level.name)

    # TODO: add function to print user-friendly formatted messages and replace all print() calls
    def log_with_ts(self, msg: str, level: Levels) -> int:
        """
        Write :param msg: to self.path_to_log if latter was passed to class constructor. Will write
        to stdin otherwise. This function also add a timestamp according to ISO. If log level requested
        is greater than the one used to create a Logger object then the message will be ignored.

        :param msg: log message to write.
        :param level: log level to tag the message.

        :return: amount of bytes written to TextIOWrapper object.
        """
        ts = datetime.datetime.now().astimezone().isoformat()
        if level <= self.level:
            if self.path_to_log is None:
                return sys.stdout.write('[{0}] {1}: {2}\n'.format(ts, self.level.name, msg))
            else:
                with open(self.path_to_log, 'rw') as f:
                    return f.write('[{0}] {1}\n'.format(self.level.name, msg))

    def log_plain(self, msg: str, level: Levels) -> int:
        """
        Write :param msg: to self.path_to_log if latter was passed to class constructor. Will write
        to stdin otherwise. If log level requested is greater than the one used to create a Logger
        object then the message will be ignored. This method won't append log level tag.

        :param msg: log message to write.
        :param level: log level to tag the message.

        :return: amount of bytes written to TextIOWrapper object.
        """
        if level <= self.level:
            if self.path_to_log is None:
                return sys.stdout.write('{0}\n'.format(msg))
            else:
                with open(self.path_to_log, 'rw') as f:
                    return f.write('[{0}] {1}\n'.format(self.level.name, msg))


if __name__ == '__main__':
    print("This module is not callable")
    sys.exit(0)
