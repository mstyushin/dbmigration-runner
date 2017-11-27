__author__ = 'Maxim Styushin'
__copyright__ = 'Copyright (c)2017, Maxim Styushin'
__license__ = 'MIT'
__email__ = 'makcimkos@gmail.com'

import sys


def generate_readme_md(config: dict) -> str:
    """
    Generate README.md for migration.

    :param config: pymigrate configuration.
    """
    template = 'MIGRATION_ID\n' \
               '======================================\n\n' \
               '### Sample README.md file for manual migration\n\n' \
               'Here goes some meaningful summary about how to run this migration. ' \
               'Note that if you keep this file, your migration will be\n' \
               'automatically marked as MANUAL.\n\n' \
               '    What\'s the point in readme if you write fully-automated migration? ;)\n\n' \
               '## Details\n\n' \
               'May be you want to describe your migration in more details?\n'

    return template.replace('MIGRATION_ID', config['MIGRATION_ID'])


def generate_migrate_sh(config: dict) -> str:
    """
    Generate migrate.sh for migration.

    :param config: pymigrate configuration.
    """
    template = '#!/bin/bash\n\n' \
               'migrate_production() {\n' \
               '  echo "This is a sample migration script"\n' \
               '  echo "Run some code to do a migration in environment {1}"\n' \
               '}\n\n' \
               '# first argument to any migrate.* script is environment name\n' \
               'case $1 in\n' \
               '  production )\n' \
               '    migrate_production\n' \
               '    ;;\n' \
               '  * )\n' \
               '    echo "Migration for environment ${1} is not implemented"\n' \
               '    exit 0\n' \
               'esac\n'

    return template


if __name__ == '__main__':
    print("This module is not callable")
    sys.exit(0)
