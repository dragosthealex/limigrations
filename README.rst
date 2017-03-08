limigrations
===============
`Migrations <https://en.wikipedia.org/wiki/Schema_migration>`_
are a type of version control for databases, used to keep track 
of the changes made, and to provide easy maintainability.
In case something goes wrong, 'rollback' can be run and it will
revert the database to the previous state.

This module provides basic migrations functionality for 
`sqlite3 <https://www.sqlite.org/>`_. It contains a method 
for connecting to the database, and functions for migrate 
and rollback.

Getting started
***************

A migration consist in a Python script (preferably named by datetime of creation)
placed in the *migrations directory*.
The script should contain an import and a class called ``Migration`` which implements ``BaseMigration``.

.. 
  from limigrations.migration import BaseMigration

  class Migration(BaseMigration):
    def up(self, conn, c):
      pass
    def down(self, conn, c):
      pass

There is an example `here <https://github.com/dragosthealex/limigrations/blob/master/migrations/example_migration.py>`_.

Installing
^^^^^^^^^^^^^^^^^^^^^
1. Install the package with `pip` or clone this repository
.. 
  pip install limigrations
  git clone git@github.com:dragosthealex/limigrations.git

2. In your project create a directory for migrations
.. 
  mkdir my-migrations
3. Decide on a name for your database e.g. *my-database.db*
.. 
  touch my-database.db

4. In *my-migrations* create your first migration, by copying the `example <https://github.com/dragosthealex/limigrations/blob/master/migrations/example_migration.py>`_
and modifying the `up` and `down` methods. Optionally, name it after the date and time e.g. *2017-03-08_12:31*

Command-Line
"""""""""""""""""
5a. Run 
.. 
  python -m limigrations migrate --db_file "my-database.db" --migrations_dir "my-migrations"
6a. Done! You should now see the changes written in the `up` method being applied.
7a. If something goes wrong and you want to revert, run
..code:: shell
  python -m limigrations rollback --db_file "my-database.db" --migrations_dir "my-migrations"
8a. You should see the changes written in the `down` method being applied.

Runtime
"""""""""""""""""
5b. Import the limigrations module and run the migrations
.. code
  from limigrations import limigrations
  
  limigrations.migrate('my-database.db', 'my-migrations')
7a. If you want to rollback later, run the rollback
.. 
  limigrations.rollback('my-database.db', 'my-migrations')
8a. If you just want to connect to the database
.. 
  conn, c = limigrations.connect_database('my-database.db')

Testing
^^^^^^^^^^^^^^^^^^^^^
After cloning the repository, run 
.. 
  python -m unittest -v tests.test_limigrations
There are two tests, one for `migrate` and one for `rollback`.
They create a test migration at runtime, defining the `up` and `down` methods,
and then call the tested functions. The tests should leave no trace, as the
directories and files are deleted after completion.

Authors
^^^^^^^^^^^^^^^^^^^^^
Alex Radu - *initial work* - `www.alexdradu.com <http://www.alexdradu.com>`_

License
^^^^^^^^^^^^^^^^^^^^^
This project is licensed under the MIT License - see the `LICENSE.md <https://github.com/dragosthealex/limigrations/blob/master/LICENSE.md>`_ file for details.
