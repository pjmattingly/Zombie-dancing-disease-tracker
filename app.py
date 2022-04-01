_DEBUG = True

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
        serialization = SerializationMiddleware(JSONStorage)
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

        from tinydb import TinyDB
        self._db = TinyDB(_path, storage=serialization)

        self._password_table = self._db.table('_passwords')
        self._data_table = self._db.table('data')

        self._password_id = 0

    def add_password(self, password):
        _p = self._create_password(password)
        self._password_table.insert({self._password_id: _p})
        self._password_id += 1

    def _create_password(self, password):
        #hash a plain-text password for storage
        #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.generate_password_hash
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password)

    def get_passwords(self): return self._get_passwords()

    def _get_passwords(self):
        return [list(row.values())[0] for row in self._password_table.all()]

    def check_password(self, password):
        return self._check_password( password, self._get_passwords() )

    def _check_password(self, password, stored_passwords):
        #hash the key and check if it's authorized
        #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.check_password_hash
        for p in stored_passwords:
            from werkzeug.security import check_password_hash
            if check_password_hash(p, password):
                return True

        return False

    def append(self, row):
        self._check_disk_usage()

        new_row = self._escape_input(row)

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

from flask import Flask
app = Flask(__name__)

from flask_restx import Api
api = Api(app)

db = Database()

#TEST
db.add_password("test")

#make a parser for the input
#see: https://flask-restx.readthedocs.io/en/latest/parsing.html
from flask_restx import reqparse
POST_parser = reqparse.RequestParser()
POST_parser.add_argument('key', required=True, help="Parameter 'key' required.")

#inherit from the GET parser to DRY
GET_parser = POST_parser.copy()

from flask_restx import Resource
from flask import request

@api.route('/log')
class Main(Resource):
    def post(self):
        args = POST_parser.parse_args()
        password = args['key']

        if not db.check_password( password ):
            from flask import abort
            abort(401, 'Incorrect key.')
        
        _input = dict(request.form)
        _input["_id"] = _input["key"]

        try:
            db.append( _input )
        except OSError as e:
            import errno
            if (e.errno == errno.ENOSPC):
                abort(507, 'Could not append to the data base as out of storage.')

        return db.__repr__()

    def get(self):
        args = GET_parser.parse_args()
        password = args["key"]

        if not db.check_password( password ):
            from flask import abort
            abort(401, 'Incorrect key.')

        search_args = dict(request.form)
        del search_args["key"]

        #if no query, then return the entire database
        if len(search_args) == 0:
            return to_JSON_safe( db.__repr__() )

        return to_JSON_safe( db.search(search_args) )

if __name__ == '__main__':
    app.run(debug=_DEBUG)