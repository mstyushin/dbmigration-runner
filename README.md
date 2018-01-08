Database schema migration runner
========================================

PyMigrate is intended to run migrations in multi-environment setup (e.g. Test + Staging + PreProduction + whatever).

### Requirements

Python >= 3.6.x

## Installation

At this moment there is no packaging done yet, so installation will be as simple as _git_ _clone_ _this_repo_.

### From this git repo

-   Clone this repo to desired location:
 
    `# git clone https://github.com/mstyushin/dbmigration-runner.git` 

-   Add _bin/_ directory in this repo to your _$PATH_

-   Go ahead and initialize migrations database in your project directory:

        $ cd /tmp/my_project
        $ pymigrate --do init
        
        [2018-01-01T23:41:50.445588+04:00] DEBUG: Config file not found, moving on
        [2018-01-01T23:41:50.445933+04:00] DEBUG: Running init action
        Initializing migrations database
        [2018-01-01T23:41:50.446049+04:00] DEBUG: Migrations directory does not exist, creating at /tmp/my_project/migrations
        [2018-01-01T23:41:50.446745+04:00] DEBUG: Initializing sqlite database
        Done!
        $

### From pypi repo

Coming soon...

How it works
------------

### Overview

The state of migrations is stored to local SQLite DB located at migrations directory.
Add *migrations.db* to your project .gitignore so each environment where project is deployed can store its own information on migrations status.
Each migration may have following states: **DONE, FAILED, MANUAL, PENDING, SKIP, UNKNOWN**.
Migration runner also monitors the branch where the migration status was changed. 

### Conventions

-   It is considered that each project has following directory layout for migrations:

        $ ls -la my_project/migrations/
        total 0
        drwxr-xr-x    6 root  wheel   192  3 Jan 23:12 .
        drwxr-xr-x   33 root  wheel  1056 14 Jan 15:26 ..
        drwxr-xr-x  122 root  wheel  3904  1 Jan 22:01 1511427379-my-migration
        drwxr-xr-x    2 root  wheel    64 16 Jan 02:02 1511437485-yet-another-migration

-   On filesystem each migration unit is essentially a directory with set of scripts required for this migration to complete.
    Consider following migration directory layout:

        1511427379-my-migration
           ----> migrate.sh - shell script for migration actions
          |
           ----> rollback.sh - shell script for rollback actions
          |
           ----> README.md - some text file with instructions on how to run this migration

-   Each migration unit should follow name convention:

    *TIMESTAMP-name-separated-with-dashes*

-   Name convention for each migration readme file is pretty simple: it should only start with *readme* string case insensitive.

### Main concepts

-   All migration directories are being sorted by their name. Timestamp in migration name ensures right order.

-   If migration status is PENDING, *migrate.sh* script will be executed.

-   If *migrate.sh* returns 0 exit code, migration is marked as DONE.

-   If *migrate.sh* returns non-zero exit code, or some failure occurs during its execution then migration is marked as FAILED.

-   If migration has status SKIP, or was DONE already, execution follows to next migration.

-   If migration has status MANUAL, the whole execution is stopped.
    You'll have to perform all necessary actions by hand and finally mark this migration as DONE by running:

    `pymigrate --do done --migration-id migration_id_with_timestamp`

-   If *readme* file is present at migration directory then this migration will be marked as MANUAL automatically.

Usage and examples
------------------

Migration runner has a help message with short description and list of all commands available and their expected arguments:

    usage: runner.py [-h] --do
                 {create,delete,done,failed,init,manual,migrate,pending,readme,rollback,skip,status}
                 [--environment ENVIRONMENT] [--project-dir PROJECT_DIR]
                 [--migration-id MIGRATION_ID]
                 [--log-level {ERROR,WARNING,INFO,DEBUG}]

Commands overview:

-   *create* - create migration unit with specified name. *migrate.sh* and *readme* files will be generated from templates.
    If you use migration name without timestamp then current timestamp will be added to your name. Example:

        pymigrate --do create -m second-migration
        
        Generating migration 1515418767-second-migration
        Done!

-   *delete* - delete migration unit with specified name. Will ask confirmation.

-   *done* - set status of specified migration to DONE.

-   *failed* - set status of specified migration to FAILED.

-   *manual* - set status of specified migration to MANUAL.

-   *pending* - set status of specified migration to PENDING.

-   *skip* - set status of specified migration to SKIP.

-   *init* - initialize SQLite database under _migrations/_ directory. Example:

        pymigrate --do init

        Initializing migrations database
        Done!

-   *migrate* - run specified migration. If _--migration-id_ is not specified then run all PENDING migrations one by one.
    Example:

        pymigrate --do migrate

        Starting migration 1511784966-first-migration
        stdout:
        Some output from migration script for 1511784966-first-migration
        Migration 1511784966-first-migration: DONE

-   *readme* - view readme file for specified migration.

-   *rollback* - run *rollback.sh* script for specified migration.

-   *status* - view status for all migrations in this project. Example:

        pymigrate --do status

        Migration summary on environment dev:
        MIGRATION_ID               | STATUS   | PRESENCE | BRANCH              
        1511784966-first-migration | PENDING  | PRESENT  | master

Options overview:

-   *--environment* - environment name the project is deployed on. Default is 'dev'.

-   *--project-dir* - path to project directory. Default is current working directory.

-   *--migration-id* - migration ID to work with. It is basically unix timestamp with dash-separated name.
    See Conventions above. If it is empty then all *PENDING* migrations will be executed one by one. 

-   *--log-level* - set logging level. All log messages will go to stderr by default.

Disclaimer
----------
This project exists only for my own educational purposes.
While some of the concepts introduced here were actually used in production and I'm trying to do my best to polish all
the functionality, I still cannot guarantee its _production readiness._ Just as usual: use at your own risk :3

License
-------
The MIT License (MIT)
