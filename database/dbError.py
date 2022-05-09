from pyodbc import DatabaseError


class SelectNoConstraintError(DatabaseError):
    pass


class NoSuchEntryError(DatabaseError):
    pass
