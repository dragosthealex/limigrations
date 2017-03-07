"""Test the limigrations module."""
import unittest
import os
import sys
import shutil
from limigrations import limigrations as limigrations


class TestLimigrations(unittest.TestCase):
  """Test case for limigrations module.

  Attributes:
    db_file (str): The path to the database file.
    migrations_dir (str): The path to the migrations directory.
  """

  def setUp(self):
    """Called before each test."""
    self.db_file = 'database.db'
    self.migrations_dir = 'migrations'
    if not os.path.isdir(self.migrations_dir):
      os.mkdir(self.migrations_dir)

  def tearDown(self):
    """Called after every test."""
    if os.path.isfile(self.migrations_dir + '/test_migration.py'):
      os.unlink(self.migrations_dir + '/test_migration.py')
    if os.path.isfile(self.db_file):
      os.unlink(self.db_file)
    if os.path.isdir(self.migrations_dir):
      shutil.rmtree(self.migrations_dir)

  def test_migrate(self):
    """Test whether the migration system works."""
    conn, c = limigrations.connect_database(self.db_file)
    # Create a migration
    with open(self.migrations_dir + "/test_migration.py", "w") as f:
      f.write("""\
def up(conn, c):
  c.execute('''CREATE TABLE IF NOT EXISTS test
               ('col1' text, 'col2' text)''')
  conn.commit()
  c.execute('''INSERT INTO test
               VALUES (?, ?)''', ('lol', 'stuff'))
  conn.commit()
def down(conn, c):
  pass""")
    # Migrate
    limigrations.migrate(self.db_file, self.migrations_dir)
    # Test whether the table was created
    c.execute("SELECT * FROM test LIMIT 1")
    row = c.fetchone()
    conn.close()
    self.assertEqual('lol', row[0])
    self.assertEqual('stuff', row[1])
    # If successful, delete the table
    conn, c = limigrations.connect_database(self.db_file)
    c.execute("DROP TABLE IF EXISTS test")
    conn.commit()
    conn.close()

  def test_migrate_rollback(self):
    """Test whether the rollback works."""
    # Create a migration
    with open(self.migrations_dir + "/test_migration.py", "w") as f:
      f.write("""\
def up(conn, c):
  c.execute('''CREATE TABLE IF NOT EXISTS test
               ('col1' text, 'col2' text)''')
  conn.commit()
  c.execute('''INSERT INTO test
               VALUES (?, ?)''', ('lol', 'stuff'))
  conn.commit()
def down(conn, c):
  c.execute('''SELECT name FROM sqlite_master
                 WHERE type="table" AND name="test"''')
  c.execute('''DROP TABLE IF EXISTS test''')
  conn.commit()""")
    # Migrate and then rollback
    limigrations.migrate(self.db_file, self.migrations_dir)
    limigrations.rollback(self.db_file, self.migrations_dir)
    # Test whether rollback works
    conn, c = limigrations.connect_database(self.db_file)
    c.execute("""SELECT name FROM sqlite_master
                 WHERE type='table' AND name='test'""")
    l = len(c.fetchall())
    conn.close()
    self.assertEqual(l, 0)
    # Delete the table if failed
    conn, c = limigrations.connect_database(self.db_file)
    c.execute("DROP TABLE IF EXISTS test")
    conn.commit()
    conn.close()
