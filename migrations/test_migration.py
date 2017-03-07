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
  conn.commit()