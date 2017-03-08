# -*- coding: utf-8 -*-
"""An example migration."""
from limigrations.migration import BaseMigration


class Migration(BaseMigration):
  """A migration for somehting."""

  def up(self, conn, c):
    """Run when calling 'migrate'."""
    # Do something with connection and cursor
    pass

  def down(self, conn, c):
    """Run when calling 'rollback'."""
    # Do something with connection and cursor
    pass
