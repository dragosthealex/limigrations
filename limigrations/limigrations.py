# -*- coding: utf-8 -*-
"""Lightweight migrations system for python / sqlite3.

Migrations are a type of version control for databases, used to
keep track of the changes made, and to provide easy maintainability.
In case something goes wrong, 'rollback' can be run and it will
revert the database to the previous state.

This module provides basic migrations functionality for sqlite3.
It contains a method for connecting to the database, a method for
creating new migrations and functions for migrate and rollback.

The migrations are stored in a migrations folder which can be
specified (default being 'migrations'). Although the date when they
are inserted in the db is stored, it is recommended to name them
by the date/time of creation.

Example:
    from limigrations import limigrations as lm
    (...)
    lm.migrate('database.db', 'migrations')
    (...)
    lm.rollback('database.db', 'migrations')

    $ python -m limigrations.limigrations new --new_migration
            "users_table_migration" --migrations_dir "migrations"
    (...)
    $ python -m limigrations.limigrations migrate --db_file "database.db"
            --migrations_dir "migrations"
    (...)
    $ python -m limigrations.limigrations rollback --db_file "database.db"
            --migrations_dir "migrations"

This module has been tested on Python 2.7 and Python 3.5

See:
https://github.com/dragosthealex/limigrations
"""
import os
import re
import sys
import time
import sqlite3
import argparse
import unicodedata
from argparse import RawTextHelpFormatter
from imp import reload

__all__ = ['connect_database', 'migrate', 'rollback']


def connect_database(db_file=None):
    """Connect to the database.

    Returns:
        The connection and a cursor
    """
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    return (conn, c)


def migrate(db_file=None, migrations_dir=None, verbose=False):
    """Run the migrations.

    Read all the migrations in the migrations directory, and add them to
    the migrations table if they are not already there. They are first inserted
    with the status 'down'.
    Then, for all migrations with status 'down', taken in chronological order,
    call the 'up' method and set their status as 'up'.

    Args:
        db_file (str, optional): The path to the database file. If not
                                provided, a new database will be created with
                                the name 'database.db'.
        migrations_dir (str, optional): The path to the migrations directory.
                                If not provided, an empty directory will be
                                created with the name 'migrations'.
    Returns:
        True if a migration was run, False otherwise.
    """
    # Create required files if not existent
    if db_file is None:  # pragma: no cover
        db_file = 'database.db'
    if migrations_dir is None:  # pragma: no cover
        migrations_dir = 'migrations'
    if not os.path.isdir(migrations_dir):  # pragma: no cover
        os.mkdir(migrations_dir)
    # Connect to db
    conn, c = connect_database(db_file)
    # Create migrations table if not existent
    c.execute('''CREATE TABLE IF NOT EXISTS migrations
                         (file text, status text, created_at datetime)''')
    conn.commit()
    # Get all migrations
    query = "SELECT * FROM migrations"
    migrations = [row[0] for row in c.execute(query)]
    # Upload the new ones
    for mig in os.listdir(migrations_dir):
        if os.path.isdir(migrations_dir + '/' + mig):  # pragma: no cover
            continue
        if re.match(r'.*\.py$', mig) is None:  # pragma: no cover
            os.unlink(migrations_dir + '/' + mig)
        elif mig not in migrations:
            if verbose:
                print("Inserting " + mig + " into migrations table ...")
            c.execute("""INSERT INTO migrations
                                     VALUES (?, ?, ?)""",
                      (mig, 'down', time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    # Add migrations to import path
    sys.path.append(migrations_dir)
    # For any migration that is down, run it
    migrations_run = 0
    for row in c.execute("""SELECT * FROM migrations
                            WHERE status='down'
                            ORDER BY datetime(created_at) DESC"""):
        # Run the up method
        if verbose:
            print("Running " + row[0] + " ...")
        mig = __import__(row[0].split('.py')[0])
        mig = reload(mig)
        mig_inst = mig.Migration()
        mig_inst.up(conn, c)
        # Modify it
        c.execute("""UPDATE migrations SET status='up'
                     WHERE file=?""", (row[0],))
        conn.commit()
        migrations_run += 1
        if verbose:
            print("Successfully run " + row[0])
    # Return the boolean
    return migrations_run > 0


def rollback(db_file=None, migrations_dir=None, verbose=False):
    """Roll back a migration.

    Calls the 'down' method of the latest migration with status
    'up'. If the migrations table does not exist, it is created.

    Args:
        db_file (str, optional): The path to the database file. If not
                                provided, a new database will be created
                                with the name 'database.db'.
        migrations_dir (str, optional): The path to the migrations directory.
                                If not provided, an empty directory will be
                                created with the name 'migrations'.
    Returns:
        True if a migration was rolled back, False otherwise.
    """
    # Create required files if not existent
    if db_file is None:  # pragma: no cover
        db_file = 'database.db'
    if migrations_dir is None:  # pragma: no cover
        migrations_dir = 'migrations'
    if not os.path.isdir(migrations_dir):  # pragma: no cover
        os.mkdir(migrations_dir)
        # No migrations, so nothing to rollback
        if verbose:
            print("No migration to roll back")
        return False
    # Connect to db and get the latest 'up' migration
    conn, c = connect_database(db_file)
    c.execute("""SELECT * FROM migrations
                 WHERE status='up'
                 ORDER BY datetime(created_at) DESC
                 LIMIT 1""")
    row = c.fetchone()
    # If nothing to run, return False
    if row is None:  # pragma: no cover
        if verbose:
            print("No migration to roll back")
        return False
    # Run the rollback
    # Add migrations to import path
    sys.path.append(migrations_dir)
    mig = __import__((row[0].split('.py'))[0])
    mig = reload(mig)
    mig_inst = mig.Migration()
    mig_inst.down(conn, c)
    # Update it
    c.execute("""UPDATE migrations SET status='down'
                 WHERE file=?""", (row[0],))
    conn.commit()
    # Something was rolled back, so return True
    return True


def new_migration(migrations_dir=None, name=None, verbose=False):
    """Create a new migration by implementing the BaseMigration."""
    if migrations_dir is None:  # pragma: no cover
        migrations_dir = 'migrations'
    if not os.path.isdir(migrations_dir):  # pragma: no cover
        os.mkdir(migrations_dir)
    name = migrations_dir + '/' + slugify(name) + '_' +\
        time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()) +\
        '.py'
    with open(name, 'w') as new_mig:
        new_mig.write("""\
# -*- coding: utf-8 -*-
\"\"\" \"\"\"
from limigrations.migration import BaseMigration


class Migration(BaseMigration):
    \"\"\"A migration for somehting.\"\"\"

    def up(self, conn, c):
        \"\"\"Run when calling 'migrate'.\"\"\"
        # Do something with connection and cursor
        pass

    def down(self, conn, c):
        \"\"\"Run when calling 'rollback'.\"\"\"
        # Do something with connection and cursor
        pass
""")
    if verbose:
        print("Migration created as " + name)
    return name


def slugify(value):
    """ Make string filename-friendly.

    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value


def main():  # pragma: no cover
    """The cmd line functionality."""
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                     prog="python -m limigrations")
    parser.add_argument("action", help="Action to take.\n" +
                        "   migrate = run all migrations in dir\n" +
                        "         -d and -m recommended\n"+
                        "   rollback = roll back the last migration\n" +
                        "         -d and -m recommended\n" +
                        "   new = create a new migration. -n required.\n" +
                        "         -m recommended",
                        choices=["migrate", "rollback", "new"])
    parser.add_argument("-n", "--new_migration", help="new migration name")
    parser.add_argument("-d", "--db_file", help="path to the database file",
                        default="database.db")
    parser.add_argument("-m", "--migrations_dir", help="path to the " +
                        "migrations directory", default="migrations")
    parser.add_argument("-v", "--verbose", help="output more info during run",
                        default="False", action="store_true")
    args = parser.parse_args()
    if args.action == 'migrate':
        result = migrate(args.db_file, args.migrations_dir, args.verbose)
        if args.verbose:
            print(result)
    elif args.action == 'rollback':
        result = rollback(args.db_file, args.migrations_dir, args.verbose)
        if args.verbose:
            print(result)
    elif args.action == 'new':
        if args.new_migration is None:
            parser.error("`new` action requires -n argument.")
        else:
            new_migration(args.migrations_dir, args.new_migration,
                          args.verbose)
if __name__ == '__main__':    # pragma: no cover
    main()
