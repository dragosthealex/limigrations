# limigrations

`Migrations<https://en.wikipedia.org/wiki/Schema_migration>` 
are a type of version control for databases, used to keep track 
of the changes made, and to provide easy maintainability.
In case something goes wrong, 'rollback' can be run and it will
revert the database to the previous state.

This module provides basic migrations functionality for 
`sqlite3<https://www.sqlite.org/>`. It contains a method 
for connecting to the database, and functions for migrate 
and rollback.

## Getting started

A migration consist in a Python script (preferably named by datetime of creation)
placed in the *migrations directory*.
The script should contain an import  a class called Migration which implements BaseMigration