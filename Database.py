class Malformed_Input(Exception):
    #see: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
    def __init__(self):
        m = 'Malformed input. Input should be of the form: -d "key=value"'
        super().__init__(m)

class Database:
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
        #hash a plain-text password for storage
        #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.generate_password_hash
        from werkzeug.security import generate_password_hash
        _p = generate_password_hash(password)

        from flask import escape
        self._user_table.insert({escape(username): _p})

    def username_exists(self, username):
        from flask import escape
        _username = escape(username)

        _users = [list(row.keys())[0] for row in self._user_table.all()]
        return (_username in _users)

    def username_has_password(self, username, password):
        from flask import escape
        _username = escape(username)

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
        self._check_disk_usage()

        new_row = self._escape_input(row)

        self._validate_input(new_row)

        from datetime import datetime
        now = datetime.now(tz=None)

        new_row["_timestamp"] = now

        self._data_table.insert( new_row )

        return self.__repr__()

    def _escape_input(self, row):
        res = dict()
        for k in row.keys():
            from flask import escape
            _k = escape(k)
            _v = escape(row[k])
            res[_k] = _v
        return res

    def _validate_input(self, row):
        for k in row.keys():
            if len(k) == 0:
                raise Malformed_Input()
            if len(row[k]) == 0:
                raise Malformed_Input()

        return row

    def search(self, q):
        safe_query = self._escape_input(q)

        from tinydb import Query
        dbq = Query()

        #return a list of rows of which the query `q` is a subset of each row
        #see: https://tinydb.readthedocs.io/en/latest/usage.html#advanced-queries
        return list( self._data_table.search(dbq.fragment( safe_query )) )

    def _check_disk_usage(self):
        import shutil
        usage = shutil.disk_usage("/")

        if ((usage.free / usage.total) <= .01):
            import errno
            raise OSError(errno.ENOSPC, "No space left on device")

    def __repr__(self):
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
    #JSON will choke on some values in the database, so convert them to JSON-safe
    #values here

    res = list()

    for row in rows:
        tmp = dict(row)
        from datetime import datetime
        tmp["_timestamp"] = row["_timestamp"].isoformat()
        res.append( tmp )

    return res