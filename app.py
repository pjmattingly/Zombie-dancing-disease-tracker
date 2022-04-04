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
db.add_user("test", "test")

#print(db._user_table.all())
#print( db.username_exists("test") )
#print( db.username_exists("some other username") )
#print( db.username_has_password("some bad username", "test") )
#print( db.username_has_password("test", "some bad password") )
#print( db.username_has_password("test", "test") )
#raise

#rate limiting to avoid swamping the server
from flask_limiter import Limiter
limiter = Limiter(
    app,
    #apply the limit to all incoming requests not just single IPs
    key_func = lambda : "",
    )

#BUG
'''
When accessing `request.json` the following error is returned for all requests:
    `code 400, message Bad request syntax`
A fix is to avoid accessing the parameter on `request`

reqparse will implicitly attempt to access request.json, and so a fix
has been applied to avoid accessing it
'''

#BUG
'''
As per Flask-restx documentation their preferred way of parsing key/value pairs
from requests is their "reqparse", but they also mark it as depreciated
with no alternative (?)
    see:
    https://flask-restx.readthedocs.io/en/latest/parsing.html
As such, using reqparse comes with a variety of subtle bugs that effect
both the main function of the code and testing
    see above
    and
    reqparse throws errors when attempting to test with Flask's
    test_request_context() method
They recommend using the `marshmallow` library, but do not provide documentation
on how to do so, and it does not seem obvious how to adapt marshmallow
to this task given the project's documentation
    see:
    https://marshmallow.readthedocs.io/en/stable/index.html
Thus, since our needs are simple for this application, such parsing has been
handled manually
'''

#TODO
#adapt marshmallow for use in validating requests
#see: https://medium.com/analytics-vidhya/building-rest-apis-using-flask-restplus-sqlalchemy-marshmallow-cff76b202bfb
#https://medium.com/craftsmenltd/flask-with-sqlalchemy-marshmallow-2ec34ecfd9d4
#https://marshmallow.readthedocs.io/en/stable/quickstart.html
class Required_Argument_Not_Found(Exception): pass
def _verify_args(args, required_keys=[]):
    _args = dict(args)
    for k in required_keys:
        if not k in _args:
            m = f"Required argument: '{k}' not found."
            raise Required_Argument_Not_Found(m)
    return _args

#custom exception for HTTP error 507
from werkzeug.exceptions import HTTPException
class InsufficientStorage(HTTPException):
    code = 507
    description = 'Insufficient Storage'

class Missing_Username_Or_Password(Exception): pass
class Bad_Username_Or_Password(Exception): pass
class Authorization_Handler:
    def __init__(self, database):
        self._db = database
        self._not_authorized_msg = "Incorrect username or password."
        self.not_authorized_msg = self._not_authorized_msg

    def _verify_authorization_present(self, request_authorization):
        #example: {'username': 'peter', 'password': 'test'}

        if (request_authorization is None) or (len(request_authorization) == 0):
            raise Missing_Username_Or_Password("Username and password required.")
            #abort(401, "Username and password required.")

        if (len(request_authorization['username']) == 0) or \
        (len(request_authorization['password']) == 0):
            raise Bad_Username_Or_Password(self._not_authorized_msg)
            #abort(401, self._not_authorized_msg)

        return request_authorization

    def _check_authorization(self, username, password):
        #hash the key and check if it's authorized
        #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.check_password_hash
        for p in stored_passwords:
            from werkzeug.security import check_password_hash
            if check_password_hash(p, password):
                return True

        return False

    def is_authorized(self, request_authorization):
        self._verify_authorization_present(request_authorization)

        _u = request_authorization['username']
        _p = request_authorization['password']

        return db.username_has_password(_u, _p)

ah = Authorization_Handler(db)

from flask_restx import Resource
@api.route('/log')
class Main(Resource):
    #apply the rate limiter to each handler
    #see: https://flask-limiter.readthedocs.io/en/stable/recipes.html#using-flask-pluggable-views
    decorators = [limiter.limit("1/second")]

    def post(self):
        from flask import request
        from flask import abort

        #TODO
        #if we need to support larger upload/POST sizes for logs we can implement
        #support for file uploading, as an alternative to using POST
        #see: https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/

        #limit POST requests to ~2GB
        #see: https://stackoverflow.com/questions/2880722/can-http-post-be-limitless
        #see: https://serverfault.com/questions/151090/is-there-a-maximum-size-for-content-of-an-http-post
        if not request.content_length is None:
            if request.content_length > 2 * 1024 * 1024 * 1024:
                #see: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.15
                abort(414)

        try:
            authorized = ah.is_authorized( request.authorization )
        except Missing_Username_Or_Password:
            abort(401, "Username and password required.")
        except Bad_Username_Or_Password:
            abort(401, ah.not_authorized_msg)
        else:
            if not authorized:
                abort(401, ah.not_authorized_msg)
        
        _input = dict(request.form)

        try:
            db.append( _input )
        except OSError as e:
            import errno
            if ( str(errno.ENOSPC) == str(e) ):
                raise InsufficientStorage('Could not append to the database as out of storage.')
            else:
                raise

        return to_JSON_safe( db.__repr__() )

    def get(self):
        from flask import request
        from flask import abort

        #limit GET requests to ~2kB
        #see: https://stackoverflow.com/questions/2659952/maximum-length-of-http-get-request
        #see: https://stackoverflow.com/questions/25036498/is-it-possible-to-limit-flask-post-data-size-on-a-per-route-basis
        if not request.content_length is None:
            if request.content_length > 2 * 1024:
                #see: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.15
                abort(414)
        
        try:
            authorized = ah.is_authorized( request.authorization )
        except Missing_Username_Or_Password:
            abort(401, "Username and password required.")
        except Bad_Username_Or_Password:
            abort(401, ah.not_authorized_msg)
        else:
            if not authorized:
                abort(401, ah.not_authorized_msg)

        search_args = dict(request.form)

        #if no query, then return the entire database
        if len(search_args) == 0:
            return to_JSON_safe( db.__repr__() )

        return to_JSON_safe( db.search(search_args) )

if __name__ == '__main__':
    app.run(debug=_DEBUG)