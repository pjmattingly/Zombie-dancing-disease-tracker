"""
The Database module

Handles database access, insertion, and search. As well as configuring the
database for optimally querying.

Custom exception classes:
Malformed_Input
Bad_Username_Or_Password
No_Such_User

Database
The main class of the module. Provides acess to the database, as well as
verifying usernames and passwords.
"""

'''
TODO
Async database operations
Tinydb is easy to work with, but doesn't allow async operations out of the box
instead we should use a more robust backend, like Redis
Redis makes async operations easy, as it comes bundled in their python library
    see:
    https://redis.io/
    https://github.com/redis/redis-py
    https://medium.com/swlh/building-rest-api-backed-by-redis-ae8ff4818460
'''

class Bad_Username_Or_Password(Exception): pass
class No_Such_User(Exception): pass

class Database:
    """
    The Database class.

    Instantiates a database, if none are present, otherwise opens a connection,
    to an existing database.
    Maintains a `_users` table, for usernames and password
    and a `data` table, for user inserted data.
    Also contains functions for inserting and querying the database.
    As well as allowing usernames and passwords to be verified with 
    stored (encrypted) user and password details.
    """
    def __init__(self, path=None):
        from pathlib import Path
        _path = Path('./')

        if not path is None:
            _path = Path(path)

        if not _path.exists():
            raise OSError(f"Path not found: {_path}")

        if _path.is_dir():
            _path = _path / "db.json"

        #adding support for timestamps to TinyDB storage
        from tinydb.storages import JSONStorage
        from tinydb_serialization import SerializationMiddleware
        from tinydb_serialization.serializers import DateTimeSerializer
        serialization_storage = SerializationMiddleware(JSONStorage)
        serialization_storage.register_serializer(DateTimeSerializer(), 'TinyDate')

        #adding support for in-memory cache to optimize for queries
        from tinydb.middlewares import CachingMiddleware
        caching_n_serialization_store = CachingMiddleware(serialization_storage)

        from tinydb import TinyDB
        self._db = TinyDB(_path, storage=caching_n_serialization_store)

        self._user_table = self._db.table('_users')
        self._data_table = self._db.table('data')

    def add_user(self, username, password):
        """
        Add a username and password to the database.
        Both arguments should be non-zero length strings.
        Passwords are encrypted, then stored. While usernames are escaped, and
        then stored.

        :param username: string
        :param password: string
        :return: None
        """
        if (len(username) == 0) or (len(password) == 0):
            raise Bad_Username_Or_Password()

        #TODO, checking for duplicate username and throwing

        #hash a plain-text password for storage
        #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.generate_password_hash
        from werkzeug.security import generate_password_hash
        _p = generate_password_hash(password)

        from flask import escape
        self._user_table.insert({escape(username): _p})

    def username_exists(self, username): return self._username_exists(username)
    
    def _username_exists(self, username):
        """
        Check if a username exists in the `_user` table

        :param username: string, the name of the user
        :return: boolean, if the username is in the `_user` table or not
        """
        from flask import escape
        _username = escape(username)

        _users = [list(row.keys())[0] for row in self._user_table.all()]
        return (_username in _users)

    def username_has_password(self, username, password):
        """
        Given a username, determine if there is a corresponding password
        associated with it.

        :param username: string
        :param password: string
        :return: boolean, whether the username is assocaited with the password
        or not.
        """
        from flask import escape
        _username = escape(username)

        if not self._username_exists(_username):
            raise No_Such_User()

        for row in self._user_table.all():
            _u = list(row.keys())[0]
            _p = list(row.values())[0]

            from werkzeug.security import check_password_hash
            _username_matches = (_username == _u)
            _password_matches = check_password_hash(_p, password)

            if _username_matches and _password_matches:
                return True

        return False

    def append(self, row):
        """
        Add a new 'row' of data to the database. A row of data is a python
        dictionary, with keys indicating column names and values indicating
        the values on that row.
        The content of the row is escaped before insertion, and an internal
        `_timestamp` value is added; Indication the time when the row
        was inserted.

        :param row: dictionary
        :return: The content of the database after insert the new row; As a list
        of dictionaries.
        """
        self._check_disk_usage()

        new_row = self._escape_input(row)

        from . import Validation_and_Standardization_Handler as vns
        vns.validate(new_row)
        new_row = vns.standardize(new_row)

        self._data_table.insert( new_row )

        return self.__repr__()

    def _escape_input(self, row):
        """
        A function to escape the content of a row of data.

        :param row: dictionary
        :return: dictionary, the escaped input
        """
        res = dict()
        for k in row.keys():
            from flask import escape
            _k = escape(k)
            _v = escape(row[k])
            res[_k] = _v
        return res

    def search(self, q):
        """
        A function to search the database for rows that containing the query `q`

        :param q: dictionary
        :return: list of dictionaries, or an empty list on not found
        """
        safe_query = self._escape_input(q)

        from tinydb import Query
        dbq = Query()

        #return a list of rows of which the query `q` is a subset of each row
        #see: https://tinydb.readthedocs.io/en/latest/usage.html#advanced-queries
        return list( self._data_table.search(dbq.fragment( safe_query )) )

    def _check_disk_usage(self):
        """
        A function to check the disk usage of the server the app is running on.
        This prevents new insertions to the database if the disk is too full
        to take them.

        :return: None
        """
        import shutil
        usage = shutil.disk_usage("/")

        if ((usage.free / usage.total) <= .01):
            import errno
            raise OSError(errno.ENOSPC, "No space left on device")

    def __repr__(self):
        """
        A convenience function to return the content of the database, ordered
        by timestamp.

        :return: list of dictionaries
        """
        _all = self._data_table.all()

        #if there are no records, then no need for sorting
        if len(_all) == 0:
            return _all

        #return a sorted list of the records in the database, sorted by timestmap
        #see: https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
        from operator import itemgetter
        return sorted(_all , key=itemgetter('_timestamp') )

    def __str__(self):
        return str(self.__repr__())

def to_JSON_safe(rows):
    '''
    A helper function to convert outputted database rows into a format that can
    be easily converted to JSON

    :param rows: list of dictionaries
    :return: sanitized list of dictionaries
    '''

    res = list()

    for row in rows:
        tmp = dict(row)
        from datetime import datetime
        tmp["_timestamp"] = row["_timestamp"].isoformat()
        res.append( tmp )

        if "date_time" in row:
            if hasattr(row["date_time"], "isoformat"):
                tmp["date_time"] = row["date_time"].isoformat()

    return res