import json
import warnings
from contextlib import AbstractContextManager
from typing import Callable, Optional, List, Dict, Any

import psycopg2
from pyodbc import Cursor

from database.dbError import SelectNoConstraintError, NoSuchEntryError


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

    class TableManager:
        def __init__(self, idb: 'SandmanPilot', table_name: str, attributes: List[str]):
            self.idb = idb
            self.table_name = table_name
            self.attributes = attributes

        def test_existence(self, constraints: Dict[str, Any]):
            if constraints is None:
                cons_str = ""
            else:
                cons_str = " WHERE " + " AND ".join([f"{attr}='{given}'" for attr, given in constraints.items()])
            stmt = f"SELECT COUNT(*) FROM {self.table_name}{cons_str};"
            self.idb.database_obj.cursor.execute(stmt)

    def __init__(self, database_obj: Database):
        self.database_obj = database_obj

    def _insert_into_table(self, table_name: str, *args, do_commit=True):
        cursor = self.database_obj.cursor
        # in the future, lets figure out a better way to do this.
        combined = ', '.join([f"'{arg}'" for arg in args])
        cursor.execute(f"EXECUTE CREATE_{table_name.upper()} ({combined});")
        if do_commit:
            self.database_obj.commit_all()

    def _select_from_table(self, table_name: str, attributes: Optional[List] = None, constraint: Optional[Dict] = None):

        attr_str = "*" if attributes is None else ", ".join(attributes)
        if constraint is None:
            raise SelectNoConstraintError(f"expected select for {table_name} to have constraint, none is give.")
        else:
            def num_or_str(ele):
                if isinstance(ele, int):
                    return str(ele)
                elif isinstance(ele, str):
                    return "'" + ele + "'"
                else:
                    raise ValueError(f"FATAL: num_or_str encountered type {str(type(ele))}, "
                                     f"dealing with table '{table_name}' currently")
            cons_str = " AND ".join([f"{attr}=" + num_or_str(given) for attr, given in constraint.items()])
        cursor = self.database_obj.cursor
        stmt = f"SELECT {attr_str} FROM {table_name.upper()} WHERE {cons_str}"
        cursor.execute(stmt)
        return cursor.fetchall()


    @str_convert(2)
    def create_server(self, server_id, owner_id):
        self._insert_into_table('SERVER', server_id, owner_id)

    @str_convert(3)
    def create_starboard(self, board_name: str, channel_id: str, server_id: str, emoji_count: int, emoji_id=None):
        # given null, any emojis go
        emoji_id = "NULL" if emoji_id is None else emoji_id
        self._insert_into_table('STARBOARD', board_name, channel_id, server_id, emoji_id, emoji_count)

    @str_convert(3)
    def create_star_message(self, msg_id, board_id, server_id):
        self._insert_into_table('STAR_MESSAGE', msg_id, board_id, server_id)

    def get_starboard(self, board_name, server_id):
        query = self._select_from_table('STARBOARD', board_name, server_id)
        if len(query) < 1:
            raise NoSuchEntryError(f"starboard '{board_name}' with server_id '{server_id}' does not exist")
        return query[0]

    def get_starboard_from_server(self, server_id):
        query = self._select_from_table('STARBOARD',
                                        attributes=["board_name", "channelid", "emojiid", "emoji_count"],
                                        constraint={"serverid": server_id})
        return query


if __name__ == '__main__':
    with open('../secret.json', 'r') as f:
        secret = json.loads(f.read())

        with Database(secret['host'],
                      'devDatabase',
                      secret['username'],
                      secret['password'],
                      prepare_location='prepare_statement.sql') as db:
            pilot = SandmanPilot(db)

            #pilot.create_server('123', '123')


