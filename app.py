_DEBUG = True

class Database:
    def __init__(self):
        self._db = {}
        self._db["_passwords"] = []
        self._db["data"] = []

    def add_password(self, password):
        self._db["_passwords"].append( self._create_password(password) )

    def _create_password(self, password):
        #hash a plain-text password for storage
        #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.generate_password_hash
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password)

    def get_passwords(self): return self._get_passwords()

    def _get_passwords(self):
        return self._db["_passwords"]

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

        #from werkzeug.exceptions import Unauthorized
        #raise Unauthorized('Incorrect key.') #401

    def append(self, row):
        self._db["data"].extend(row)
        return self._db["data"]

    def __repr__(self):
        res = {}
        #avoid exposing internal database keys (that start with _)
        for key in self._db.keys():
            if not str(key).startswith("_"):
                res[key] = self._db[key]
        
        return res

from flask import Flask
app = Flask(__name__)

from flask_restx import Api
api = Api(app)

db = Database()

#TEST
db.add_password("test")

def check_input_format(request_form):
    from werkzeug.exceptions import BadRequest
    if not "data" in request_form:
        raise BadRequest("Parameter 'data' is required.") #400

    from werkzeug.exceptions import Unauthorized
    if not "key" in request_form:
        #instead of using the flask abort() use the internal exceptions
        #see: https://flask.palletsprojects.com/en/2.1.x/errorhandling/
        #https://werkzeug.palletsprojects.com/en/2.1.x/exceptions/
        raise BadRequest("Parameter 'key' required.") #400

from flask_restx import Resource
from flask import request

@api.route('/log')
class Main(Resource):
    def post(self):
        check_input_format(request.form)
        
        password = request.form['key']
        if not db.check_password( password ):
            flask.abort(401, 'Incorrect key.')
        
        from flask import escape
        db.append( escape( request.form['data'] ) )

        return db.__repr__()

    def get(self):
        #TODO, checking for "key" parameter here

        if not db.check_password( password ):
            flask.abort(401, 'Incorrect key.')

        return db.__repr__()

if __name__ == '__main__':
    app.run(debug=_DEBUG)