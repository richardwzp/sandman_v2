import json
import warnings
from contextlib import AbstractContextManager
from typing import Callable

import psycopg2
from pyodbc import Cursor


class Database(AbstractContextManager):
    def __init__(self, host, database, username, password,
                 prepare_location='database/prepare_statement.sql'):
        self._conn = \
            psycopg2.connect(
                host=host,
                database=database,
                user=username,
                password=password)
        self._cursor = self._conn.cursor()
        self._has_commit = True
        self._database_location = prepare_location

    def __enter__(self):
        # execute all prepare statement, load them into this session
        with open(self._database_location, 'r') as f:
            sts = f.read()
            sts = sts.split(";")
        for st in sts:
            if st:
                self.cursor.execute(st)
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


def str_convert(amount: int) -> Callable:
    """convert a prefix amount of argument to string"""

    def deco_wrapper(func):
        def wrapper(*args, **kwargs):
            args = [i for i in args]
            if len(args) < amount:
                raise ValueError(f"this wrapper expects to convert "
                                 f"{amount} argument, function only has {len(args)}")
            # start at 1 to avoid self parameter
            for i in range(1, amount):
                args[i] = str(args[i])
            return func(*args, **kwargs)

        return wrapper

    return deco_wrapper


class SandmanPilot:
    """
    A pilot class for the database.
    It's recommended that relevant operations are implemented in this class,
    or as a subclass of this class.
    """
    __slots__ = 'database_obj'

    def __init__(self, database_obj: Database):
        self.database_obj = database_obj

    @str_convert(2)
    def create_server(self, server_id, owner_id):
        cursor = self.database_obj.cursor
        # in the future, lets figure out a better way to do this.
        cursor.execute(f"EXECUTE CREATE_SERVER ('{server_id}', '{owner_id}');")

        self.database_obj.commit_all()

    @str_convert(2)
    def create_starboard(self, channel_id, server_id):
        cursor = self.database_obj.cursor
        # in the future, lets figure out a better way to do this.
        cursor.execute(f"EXECUTE CREATE_STARBOARD ('{channel_id}', '{server_id}');")


if __name__ == '__main__':
    with open('../secret.json', 'r') as f:
        secret = json.loads(f.read())

        with Database(secret['host'],
                      'devDatabase',
                      secret['username'],
                      secret['password'],
                      prepare_location='prepare_statement.sql') as db:
            pilot = SandmanPilot(db)
            pilot.create_server('123', '123')

