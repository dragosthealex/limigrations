"""Lightweight migrations system for python / sqlite3."""
import os
import sys
import time
import sqlite3
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


def migrate(db_file=None, migrations_dir=None):
  """Run the migrations.

  Read all the migrations in the migrations directory, and add them to
  the migrations table if they are not already there. They are first inserted
  with the status 'down'.
  Then, for all migrations with status 'down', taken in chronological order,
  call the 'up' method and set their status as 'up'.

  Args:
    db_file (str, optional): The path to the database file. If not provided,
                             a new database will be created with the name
                             'database.db'.
    migrations_dir (str, optional): The path to the migrations directory. If
                                    not provided, an empty directory will be
                                    created with the name 'migrations'.
  Returns:
    True if a migration was run, False otherwise.
  """
  # Create required files if not existent
  if db_file is None:
    db_file = 'database.db'
  if migrations_dir is None:
    migrations_dir = 'migrations'
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
    if mig not in migrations:
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
                          ORDER BY date(created_at) DESC"""):
    # Run the up method
    mig = __import__(row[0].split('.py')[0])
    mig = reload(mig)
    mig.up(conn, c)
    # Modify it
    c.execute("""UPDATE migrations SET status='up'
                 WHERE file=?""", (row[0],))
    conn.commit()
    migrations_run += 1
  # Return the boolean
  return migrations_run > 0


def rollback(db_file=None, migrations_dir=None):
  """Roll back a migration.

  Calls the 'down' method of the latest migration with status
  'up'. If the migrations table does not exist, it is created.

  Args:
    db_file (str, optional): The path to the database file. If not provided,
                             a new database will be created with the name
                             'database.db'.
    migrations_dir (str, optional): The path to the migrations directory. If
                                    not provided, an empty directory will be
                                    created with the name 'migrations'.
  Returns:
    True if a migration was rolled back, False otherwise.
  """
  # Create required files if not existent
  if db_file is None:
    db_file = 'database.db'
  if migrations_dir is None:
    migrations_dir = 'migrations'
    os.mkdir(migrations_dir)
    # No migrations, so nothing to rollback
    return False
  # Connect to db and get the latest 'up' migration
  conn, c = connect_database(db_file)
  c.execute("""SELECT * FROM migrations
               WHERE status='up'
               ORDER BY date(created_at) DESC
               LIMIT 1""")
  row = c.fetchone()
  # If nothing to run, return False
  if row is None:
    return False
  # Run the rollback
  mig = __import__((row[0].split('.py'))[0])
  mig = reload(mig)
  mig.down(conn, c)
  # Update it
  c.execute("""UPDATE migrations SET status='down'
                 WHERE file=?""", (row[0],))
  conn.commit()
  # Something was rolled back, so return True
  return True
