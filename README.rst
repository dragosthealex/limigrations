limigrations
===============
`Migrations <https://en.wikipedia.org/wiki/Schema_migration>`_
are a type of version control for databases, used to keep track 
of the changes made, and to provide easy maintainability.
In case something goes wrong, 'rollback' can be run and it will
revert the database to the previous state.

`limigrations <https://pypi.python.org/pypi/limigrations/1.0.0>`_ provides basic migrations functionality for 
`sqlite3 <https://www.sqlite.org/>`_. It contains a method 
for connecting to the database, and functions for migrate 
and rollback.

Getting started
***************

A migration consist in a Python script (preferably named by datetime of creation)
placed in the *migrations directory*.
The script should contain an import and a class called ``Migration`` which implements ``BaseMigration``.
::
  from limigrations.migration import BaseMigration

  class Migration(BaseMigration):
    def up(self, conn, c):
      pass
    def down(self, conn, c):
      pass

There is an example `here <https://github.com/dragosthealex/limigrations/blob/master/migrations/example_migration.py>`_.

Instalation
^^^^^^^^^^^^^^^^^^^^^
Install the package with `pip`
:: 
  $ pip install limigrations
or clone this repository and install
::
  $ git clone git@github.com:dragosthealex/limigrations.git
  $ python setup.py install

Usage
^^^^^^^^^^^^^^^^^^^^^

1. In your project create a directory for migrations
:: 
  $ mkdir my-migrations
2. Decide on a name for your database e.g. *my-database.db*
:: 
  $ touch my-database.db

3. In *my-migrations* create your first migration, by copying the `example <https://github.com/dragosthealex/limigrations/blob/master/migrations/example_migration.py>`_
and modifying the `up` and `down` methods. Optionally, name it after the date and time e.g. *2017-03-08_12:31*

Command-Line
"""""""""""""""""
4a. Run
:: 
  $ python -m limigrations migrate --db_file "my-database.db" --migrations_dir "my-migrations"
5a. Done! You should now see the changes written in the `up` method being applied.

6a. If something goes wrong and you want to revert, run
:: 
  $ python -m limigrations rollback --db_file "my-database.db" --migrations_dir "my-migrations"
7a. You should see the changes written in the `down` method being applied.

Options
~~~~~~~~~~~~~~~~
The following options can be used:
::
    $ python -m limigrations -h

    usage: limigrations.py [-h] [-d DB_FILE] [-m MIGRATIONS_DIR] [-v] action

    positional arguments:
      action                Action to take, can be 'migrate' or 'rollback'

    optional arguments:
      -h, --help            show this help message and exit
      -d DB_FILE, --db_file DB_FILE
                            Path to the database file.
      -m MIGRATIONS_DIR, --migrations_dir MIGRATIONS_DIR
                            Path to the migrations directory.
      -v, --verbose         Verbose

Runtime
"""""""""""""""""
4b. Import the limigrations module and run the migrations
::  
  from limigrations import limigrations
  
  limigrations.migrate('my-database.db', 'my-migrations')
5a. If you want to rollback later, run the rollback
:: 
  limigrations.rollback('my-database.db', 'my-migrations')
6a. If you just want to connect to the database
:: 
  conn, c = limigrations.connect_database('my-database.db')

Testing
***************
After cloning the repository, run 
:: 
  python -m unittest -v tests.test_limigrations
There are two tests, one for `migrate` and one for `rollback`.
They create a test migration at runtime, defining the `up` and `down` methods,
and then call the tested functions. The tests should leave no trace, as the
directories and files are deleted after completion.

Contributing
***************
1. Fork the `repository <https://github.com/pypa/twine>`_ on GitHub.
2. Make a branch off of master and commit your changes to it.
3. Run the tests with ``unittest``  
4. Ensure that your name is added to the end of the AUTHORS file using the
   format ``Name <email@domain.com> (url)``, where the ``(url)`` portion is
   optional.
5. Submit a Pull Request to the master branch on GitHub.

If you'd like to have a development environment, you should create a
virtualenv and then do ``pip install -e .`` from within the directory.

Authors
***************
Alex Radu - *initial work* - `www.alexdradu.com <http://www.alexdradu.com>`_

License
***************
This project is licensed under the MIT License - see the `LICENSE.md <https://github.com/dragosthealex/limigrations/blob/master/LICENSE.md>`_ file for details.
