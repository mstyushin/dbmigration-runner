__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import os
import sys
import migration
import logger
import util
"""
Don't use imports like 'from modulename import something', since currently this module must contain
action callables only.
"""


def init(config: dict, app_logger: logger.Logger) -> bool:
    """
    Initialize sqlite3 database with migrations metadata.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running init action', logger.Levels.DEBUG)
    print("Initializing migrations database")
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    res = migration.db_init(migrations_directory_path, app_logger)
    print("Done!")

    return res


# TODO: implement pagination
def status(config: dict, app_logger: logger.Logger) -> bool:
    """
    Print to stdout formatted table with status for all migrations.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running status action', logger.Levels.DEBUG)
    print('Migration summary on environment {0}:'.format(config['ENVIRONMENT']))

    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    if not os.path.isfile(migrations_directory_path + '/migrations.db'):
        migration.db_init(migrations_directory_path, app_logger)
    migration_statuses = migration.get_statuses(migrations_directory_path + '/migrations.db', app_logger)

    # generate template with alignments for pretty-printing
    spaces = max(len(x) for x in migration_statuses.keys()) if len(migration_statuses) != 0 else 4
    line_template = '%-' + str(spaces) + 's | %-8s | %-8s | %-20s'

    print(line_template % ('MIGRATION_ID', 'STATUS', 'PRESENCE', 'BRANCH'))
    for migration_id, state in sorted(migration_statuses.items()):
        print(line_template % (migration_id, state[0], state[1], state[2]))
    return True


def done(config: dict, app_logger: logger.Logger) -> bool:
    """
    Set migration status to DONE.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running status_done action for migration {0}'.format(config['MIGRATION_ID']),
                           logger.Levels.DEBUG)
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    return migration.set_status_done(config['MIGRATION_ID'], app_logger, migrations_directory_path)


def skip(config: dict, app_logger: logger.Logger) -> bool:
    """
    Set migration status to SKIP.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running status_skip action for migration {0}'.format(config['MIGRATION_ID']),
                           logger.Levels.DEBUG)
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    return migration.set_status_skip(config['MIGRATION_ID'], app_logger, migrations_directory_path)


def failed(config: dict, app_logger: logger.Logger) -> bool:
    """
    Set migration status to FAILED.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running status_failed action for migration {0}'.format(config['MIGRATION_ID']),
                           logger.Levels.DEBUG)
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    return migration.set_status_failed(config['MIGRATION_ID'], app_logger, migrations_directory_path)


def pending(config: dict, app_logger: logger.Logger) -> bool:
    """
    Set migration status to PENDING.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running status_pending action for migration {0}'.format(config['MIGRATION_ID']),
                           logger.Levels.DEBUG)
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    return migration.set_status_pending(config['MIGRATION_ID'], app_logger, migrations_directory_path)


def manual(config: dict, app_logger: logger.Logger) -> bool:
    """
    Set migration status to MANUAL.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running status_manual action for migration {0}'.format(config['MIGRATION_ID']),
                           logger.Levels.DEBUG)
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    return migration.set_status_manual(config['MIGRATION_ID'], app_logger, migrations_directory_path)


def readme(config: dict, app_logger: logger.Logger) -> bool:
    """
    Display contents of readme file located within migration directory. Return False if readme file doesn't exist.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running readme action', logger.Levels.DEBUG)

    migration_dir = os.path.join(os.pardir, config['PROJECT_DIR'] +
                                 '/' + config['MIGRATIONS_DIR'] +
                                 '/' + config['MIGRATION_ID'])

    readme_files = util.find_files('readme*', migration_dir, False)
    if len(readme_files) != 0:
        for readme_file in readme_files:
            with open(readme_file, 'r') as f:
                print("Contents of {0}".format(readme_file))
                print(f.read())
    else:
        app_logger.log_with_ts("No readme files found", logger.Levels.ERROR)
        return False
    return True


def migrate(config: dict, app_logger: logger.Logger) -> bool:
    """
    Run migration. If :param config['MIGRATION_ID']: is not specified, then run all PENDING migrations starting from
    older one. If one of migrations fails then stop execution and return False.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running migrate action', logger.Levels.DEBUG)
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])

    if not config['MIGRATION_ID']:
        migrations_dict = migration.get_statuses(migrations_directory_path + '/migrations.db', app_logger)
        for migration_id, state in sorted(migrations_dict.items()):
            if state[1] == 'ABSENT':
                continue
            elif state[0] == migration.Status.DONE.name:
                continue
            elif state[0] == migration.Status.SKIP.name:
                continue

            print('Starting migration {0}'.format(migration_id))
            if migration.run_migration(migration_id, config, app_logger):
                print('Migration {0}: {1}'.format(migration_id, migration.Status.DONE.name))
            else:
                print('Migration {0}: {1}'.format(migration_id, migration.Status.FAILED.name))
                return False
    else:
        # TODO: check for migration state as done above (i.e. was it already DONE or set to SKIP, is it ABSENT)
        migration_id = config['MIGRATION_ID']
        if migration.run_migration(migration_id, config, app_logger):
            print('Migration {0}: {1}'.format(migration_id, migration.Status.DONE.name))
        else:
            print('Migration {0}: {1}'.format(migration_id, migration.Status.FAILED.name))
            return False
    return True


def rollback(config: dict, app_logger: logger.Logger) -> bool:
    """
    Rollback a migration.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running rollback action', logger.Levels.DEBUG)
    return True


def create(config: dict, app_logger: logger.Logger) -> bool:
    """
    Generate new migration from predefined template.
    Current unix timestamp will be prepended to resulting migration ID.

    Note that migration ID string has following form:
        UNIXTIMESTAMP-SOMESTRING
    e.g. 1511081545-myAwesomeMigration

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running create action', logger.Levels.DEBUG)
    return migration.create_migration(config, app_logger)


def delete(config: dict, app_logger: logger.Logger) -> bool:
    """
    Delete migration from disk and from migrations database as well. Will ask confirmation.

    :param config: pymigrate configuration.
    :param app_logger: pymigrate configured logger.

    :return: True on success, False otherwise.
    """
    app_logger.log_with_ts('Running delete action', logger.Levels.DEBUG)
    migration_id = config['MIGRATION_ID']
    if util.query_yes_no('Are you sure you want to delete {0} ?'.format(migration_id)):
        migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
        if migration.delete_migration(migration_id, migrations_directory_path, app_logger):
            print('Deleted {0}'.format(migration_id))
        else:
            return False
    else:
        print("Aborting")
        return True

    return True


if __name__ == '__main__':
    print("This module is not callable")
    sys.exit(0)
