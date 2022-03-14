import warnings
from contextlib import AbstractContextManager

import psycopg2
from psycopg2 import connection


class Database(AbstractContextManager):
    def __init__(self, host, database, username, password):
        self._conn: connection = \
            psycopg2.connect(
                host=host,
                database=database,
                user=username,
                password=password)
        self._cursor = self._conn.cursor()
        self._has_commit = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._has_commit:
            warnings.warn("exiting without commiting, is this intentional?")
            self._cursor.close()
            self._conn.close()

    @property
    def cursor(self):
        return self._cursor

    def commit_all(self):
        self._conn.commit()
        self._cursor.close()
        self._cursor = self._conn.cursor()
        self._has_commit = True


