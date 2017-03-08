# -*- coding: utf-8 -*-
"""The template for a migration.

The migrations folder should contain python scripts that contain
a single class which extends this migration and implements the
methods up and down.

Example:
  from limigrations.migration import BaseMigration
  (...)
  class Migration(BaseMigration):
    def up(self, db_file=None, migrations_dir=None):
      # called on migrate
      pass

    def down(self, conn, c):
      # called on rollback
      pass
"""
from six import add_metaclass
from abc import ABCMeta, abstractmethod

__all__ = ['BaseMigration']


@add_metaclass(ABCMeta)
class BaseMigration():

  @abstractmethod
  def up(self, conn, c): pass

  @abstractmethod
  def down(self, conn, c): pass