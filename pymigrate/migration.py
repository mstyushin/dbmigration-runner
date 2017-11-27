__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import sys
import os
import sqlite3
import git
import logger
import shutil
import util
import time
import templates
import io
import subprocess
from enum import Enum
from enum import auto


class Status(Enum):
    """
    Enum representing possible migration states.
    """
    DONE = auto()
    FAILED = auto()
    MANUAL = auto()
    PENDING = auto()
    SKIP = auto()
    UNKNOWN = auto()


def set_status(migration_id: str, path_to_db_dir: str, status: Status, app_logger: logger.Logger) -> bool:
    """
    Mark current migration as :param mark: in sqlite database. Return True on success.

    :param migration_id: migration name (without extension)
    :param path_to_db_dir: absolute path to sqlite database with migrations metadata
    :param status: how to mark a migration. Possible values are covered by :type migration.Status: enum.
    :param app_logger: pymigrate configured logger

    :return: True on success, False otherwise
    """
    query_template = "UPDATE migrations SET migration_id='{0}', branch='{1}', status='{2}' where migration_id='{3}'"

    if not path_to_db_dir:
        db = os.path.dirname(os.path.realpath(__file__)) + '/' + os.path.join(os.pardir, 'migrations.db')
        if not os.path.isfile(db):
            db_init(os.path.dirname(db), app_logger)
        branch = git.get_branch(os.path.dirname(db))
    else:
        db = path_to_db_dir + '/migrations.db'
        if not os.path.isfile(db):
            db_init(path_to_db_dir, app_logger)
        branch = git.get_branch(path_to_db_dir)

    if check_status(migration_id, db, app_logger) == 'UNKNOWN':
        print("Migration not found: %s" % migration_id)
        return False
    with sqlite3.connect(db) as conn:
        c = conn.cursor()
        c.execute(query_template.format(migration_id, branch, status.name, migration_id))
        conn.commit()
    return True


def set_status_done(migration_id, app_logger: logger.Logger, path_to_db_dir=None) -> bool:
    """
    Set status of migration with :param migration_id: to DONE in sqlite database.

    :param migration_id: ID of migration to work with
    :param app_logger: pymigrate configured logger
    :param path_to_db_dir: absolute path to directory containing migrations.db database file

    :return: True on success, False otherwise
    """
    return set_status(migration_id, path_to_db_dir, Status.DONE, app_logger)


def set_status_failed(migration_id, app_logger: logger.Logger, path_to_db_dir=None) -> bool:
    """
    Set status of migration with :param migration_id: to FAILED in sqlite database.

    :param migration_id: ID of migration to work with
    :param app_logger: pymigrate configured logger
    :param path_to_db_dir: absolute path to directory containing migrations.db database file

    :return: True on success, False otherwise
    """
    return set_status(migration_id, path_to_db_dir, Status.FAILED, app_logger)


def set_status_manual(migration_id, app_logger: logger.Logger, path_to_db_dir=None) -> bool:
    """
    Set status of migration with :param migration_id: to MANUAL in sqlite database.

    :param migration_id: ID of migration to work with
    :param app_logger: pymigrate configured logger
    :param path_to_db_dir: absolute path to directory containing migrations.db database file

    :return: True on success, False otherwise
    """
    return set_status(migration_id, path_to_db_dir, Status.MANUAL, app_logger)


def set_status_skip(migration_id, app_logger: logger.Logger, path_to_db_dir=None) -> bool:
    """
    Set status of migration with :param migration_id: to SKIP in sqlite database.

    :param migration_id: ID of migration to work with
    :param app_logger: pymigrate configured logger
    :param path_to_db_dir: absolute path to directory containing migrations.db database file

    :return: True on success, False otherwise
    """
    return set_status(migration_id, path_to_db_dir, Status.SKIP, app_logger)


def set_status_pending(migration_id, app_logger: logger.Logger, path_to_db_dir=None) -> bool:
    """
    Set status of migration with :param migration_id: to PENDING in sqlite database.

    :param migration_id: ID of migration to work with
    :param app_logger: pymigrate configured logger
    :param path_to_db_dir: absolute path to directory containing migrations.db database file

    :return: True on success, False otherwise
    """
    return set_status(migration_id, path_to_db_dir, Status.PENDING, app_logger)


def check_status(migration_id: str, path_to_db: str, app_logger: logger.Logger) -> Status:
    """
    Read status of migration :param migration_id:
    If migrations database has not been initialized yet, return Status.PENDING.

    :param migration_id: migrationId string
    :param path_to_db: full path to database file
    :param app_logger: instance of configured logger

    :return: :type migration.Status: of migration :param migration_id:
    """
    query = "SELECT status from migrations where migration_id='{0}'"

    if not os.path.isfile(path_to_db):
        app_logger.log_with_ts("DB not found: {0}".format(path_to_db), logger.Levels.INFO)
        return Status.PENDING

    # TODO: handle io, sqlite db exceptions
    with sqlite3.connect(path_to_db) as conn:
        c = conn.cursor()
        res = c.execute(query.format(migration_id)).fetchone()[0].replace('\n', '')
        return Status.__members__[res] if res and res in Status.__members__ else Status.UNKNOWN


def get_statuses(path_to_db: str, app_logger: logger.Logger) -> dict:
    """
    Generate key-value pairs by selecting all rows from migrations table thus presenting
    a migration status summary.

    :param path_to_db: absolute path to sqlite db file
    :param app_logger: instance of configured logger

    :return: dict where key is migrationId and value is a tuple of all the rest columns
    """
    res = {}
    with sqlite3.connect(path_to_db) as conn:
        stmt = 'SELECT * from migrations ORDER BY migration_id'
        try:
            # TODO: deal with potentially big migrations table
            from_db = dict({(lambda t: (t[0], tuple(t[1:])))(row) for row in conn.cursor().execute(stmt)})
            # TODO: need more elegant solution here
            if len(from_db) != 0:
                res = from_db
        except sqlite3.OperationalError:
            app_logger.log_with_ts('Migrations database not found at: {0}'.format(path_to_db), logger.Levels.WARNING)
        finally:
            return res


# TODO: add some debug logging here
def db_init(path_to_db_dir: str, app_logger: logger.Logger) -> bool:
    """
    Initialize sqlite3 database with migrations metadata at given absolute path.

    :param path_to_db_dir: absolute path to migrations directory
    :param app_logger: instance of configured logger

    :return: True on success, False otherwise
    """
    if not os.path.isdir(path_to_db_dir):
        app_logger.log_with_ts('Migrations directory does not exist, creating at {0}'.format(path_to_db_dir),
                               logger.Levels.WARNING)
        os.makedirs(path_to_db_dir, 0o775)
    migration_names = [migration for migration in os.listdir(path_to_db_dir) if
                       os.path.isdir(os.path.join(path_to_db_dir, migration))]
    # TODO: handle io, sqlite db exceptions
    with sqlite3.connect(path_to_db_dir + '/migrations.db') as conn:
        app_logger.log_with_ts('Initializing sqlite database', logger.Levels.DEBUG)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS migrations (migration_id, status, presence, branch)')
        branch = git.get_branch(path_to_db_dir)
        for migration_id in migration_names:
            c.execute("INSERT INTO migrations VALUES ('{0}', 'PENDING', 'PRESENT', '{1}')".format(migration_id, branch))
        conn.commit()
    return True


# TODO: Do we really need to pass config dict here or it'd be better to do as in db_init function
# TODO: add some debug logging here
# TODO: consider using this function as a context manager
def db_update(config: dict, app_logger: logger.Logger) -> bool:
    """
    Check migrations directory for new migrations since last run and update migrations database.

    :param config: pymigrate configuration
    :param app_logger: instance of configured logger

    :return:
    """
    app_logger.log_with_ts('Starting migration database update process', logger.Levels.DEBUG)
    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    migration_ids = [migration_id for migration_id in os.listdir(migrations_directory_path) if
                     os.path.isdir(os.path.join(migrations_directory_path, migration_id))]

    migrations_from_db = get_statuses(migrations_directory_path + '/migrations.db', app_logger)
    branch = git.get_branch(migrations_directory_path)
    app_logger.log_with_ts('Got git branch: {0}'.format(branch), logger.Levels.DEBUG)

    # TODO: handle io, sqlite db exceptions
    with sqlite3.connect(migrations_directory_path + '/migrations.db') as conn:
        c = conn.cursor()
        for migration_id, status in migrations_from_db.items():
            if migration_id not in migration_ids:
                app_logger.log_with_ts('Migration {0} is missing on disk, marking it ABSENT'.format(migration_id),
                                       logger.Levels.DEBUG)
                c.execute(
                    "UPDATE migrations SET presence='ABSENT' where migration_id='{0}'".format(migration_id))
            elif migration_id not in migration_ids and status == 'ABSENT':
                app_logger.log_with_ts('Migration re-appeared: {0}'.format(migration_id), logger.Levels.DEBUG)
                c.execute("UPDATE migrations SET presence='PRESENT' where migration_id='{0}'".format(migration_id))

        for migration_id in migration_ids:
            if migration_id not in migrations_from_db:
                app_logger.log_with_ts('New migration detected: {0}'.format(migration_id), logger.Levels.DEBUG)
                c.execute(
                    "INSERT INTO migrations VALUES ('{0}', 'PENDING', 'PRESENT', '{1}')".format(migration_id, branch))

            # Set migration status MANUAL if readme.* is present
            check_query = "SELECT status from migrations where migration_id='{0}'"
            readme_files = util.find_files('readme*', migrations_directory_path + '/' + migration_id, False)
            if len(readme_files) != 0 and os.path.isfile(readme_files[0]) and \
                            c.execute(check_query.format(migration_id)).fetchone()[0].replace('\n', '') not in (
                            Status.DONE.name, Status.FAILED.name, Status.SKIP.name):
                app_logger.log_with_ts('Readme file detected for migration: {0}'.format(migration_id),
                                       logger.Levels.DEBUG)
                c.execute("UPDATE migrations SET status='MANUAL' where migration_id='{0}'".format(migration_id))
    return True


# TODO: handle sql exceptions
def delete_migration(migration_id: str, migrations_directory_path: str, app_logger: logger.Logger) -> bool:
    """
    Delete specified migration from database.

    :param migration_id: MIGRATION_ID to delete from sqlite db
    :param db_path: absolute path to migrations directory
    :param app_logger: instance of configured logger
    """
    db = migrations_directory_path + '/migrations.db'
    if os.path.isfile(db):
        delete_query = "DELETE from migrations WHERE migration_id='{0}'".format(migration_id)

        with sqlite3.connect(db) as conn:
            c = conn.cursor()
            app_logger.log_with_ts('Executing query:\n{0}'.format(delete_query), logger.Levels.DEBUG)
            c.execute(delete_query)
            conn.commit()

    try:
        shutil.rmtree(migrations_directory_path + '/' + migration_id)
        app_logger.log_with_ts('Deleted {0}'.format(migration_id), logger.Levels.DEBUG)
    except OSError:
        app_logger.log_with_ts('Failed to delete migration {0}'.format(migration_id), logger.Levels.ERROR)
        return False

    return True


def create_migration(config: dict, app_logger: logger.Logger) -> bool:
    """
    Create directory for migration config['MIGRATION_ID'] and fill it with templates.

    :param config: pymigrate configuration
    :param app_logger: instance of configured logger
    """
    cur_timestamp = int(time.time())
    # try to extract timestamp from migration name
    try:
        ts = int(config['MIGRATION_ID'].split('-')[0])
        if abs(cur_timestamp - ts) <= 10000000:
            migration_id = config['MIGRATION_ID']
        else:
            if util.query_yes_no('Are you sure with timestamp? {0} '.format(ts)):
                migration_id = config['MIGRATION_ID']
            else:
                return False
    except ValueError:
        app_logger.log_with_ts('Unable to extract timestamp from provided MIGRATION_ID, '
                               'will append current timestamp', logger.Levels.DEBUG)
        migration_id = str(cur_timestamp) + '-' + config['MIGRATION_ID']

    migrations_directory_path = os.path.join(os.pardir, config['PROJECT_DIR'] + '/' + config['MIGRATIONS_DIR'])
    new_migration_path = migrations_directory_path + '/' + migration_id
    print("Generating migration {0}".format(migration_id))
    try:
        os.mkdir(new_migration_path, 0o775)
        # TODO: think about module paths for templates
        # TODO: do replacements in templates more elegantly
        with open(new_migration_path + '/README.md', mode='w') as f:
            f.write(templates.generate_readme_md(config))
        with open(new_migration_path + '/migrate.sh', mode='w') as f:
            f.write(templates.generate_migrate_sh(config))

        os.chmod(new_migration_path + '/migrate.sh', 0o775)

        if db_update(config, app_logger):
            print("Done!")
        else:
            app_logger.log_with_ts("Failed to update migrations db", logger.Levels.ERROR)
    except OSError:
        print("Failed to create migration {0}".format(migration_id))
        return False


def run_migration(migration_id: str, config: dict, app_logger: logger.Logger) -> bool:
    """
    Run migration :param migration_id:.

    :param migration_id: id of migration to run
    :param config: pymigrate configuration
    :param app_logger: instance of configured logger
    """
    migration_dir = os.path.join(os.pardir, config['PROJECT_DIR'] +
                                 '/' + config['MIGRATIONS_DIR'] +
                                 '/' + migration_id)
    app_logger.log_with_ts("Running migration {0} from directory {1}".format(migration_id, migration_dir),
                           logger.Levels.DEBUG)

    # we do not expect more than one migrate* exec
    # TODO: may be we shall exec only migrate.sh if it exists and don't touch other migrate* executables there
    migrate_executable = util.find_files('migrate*', migration_dir, True).pop()
    tmp_file = '/tmp/.migration_runner_stream.tmp'
    cmd = migrate_executable + " {0} ".format(config['ENVIRONMENT'])
    with io.open(tmp_file, 'wb') as writer, io.open(tmp_file, 'rb', 1) as reader:
        child = subprocess.Popen(cmd,
                                 shell=True,
                                 stdout=writer,
                                 stderr=subprocess.STDOUT,
                                 env=config)
        print('stdout:')
        while child.poll() is None:
            print(reader.read())
            time.sleep(0.5)
        print(reader.read())
        exit_code = child.returncode
        app_logger.log_with_ts("Migration executable exit code: {0}".format(exit_code), logger.Levels.DEBUG)
        os.remove(tmp_file)

    if int(exit_code) == 0:
        app_logger.log_with_ts("Migration is considered DONE", logger.Levels.DEBUG)
        set_status_done(migration_id, app_logger, os.path.join(os.pardir,
                                                               config['PROJECT_DIR'] + '/' +
                                                               config['MIGRATIONS_DIR']))
        return True
    else:
        app_logger.log_with_ts("Migration is considered FAILED", logger.Levels.DEBUG)
        set_status_failed(migration_id, app_logger, os.path.join(os.pardir,
                                                                 config['PROJECT_DIR'] + '/' +
                                                                 config['MIGRATIONS_DIR']))
        return False


if __name__ == '__main__':
    print("This module is not callable")
    sys.exit(0)
