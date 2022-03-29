_DEBUG = True

from flask import Flask
app = Flask(__name__)

from flask_restx import Api
api = Api(app)

db = {}
db["_passwords"] = []

def create_password(password):
    #hash a plain-text password for storage
    #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.generate_password_hash
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

#TEST
db["_passwords"].append( create_password("test") )

def check_for_access(request_form, passwords):
    from werkzeug.exceptions import Unauthorized

    if not "key" in request_form:
        #instead of using the flask abort() use the internal exceptions
        #see: https://flask.palletsprojects.com/en/2.1.x/errorhandling/
        #https://werkzeug.palletsprojects.com/en/2.1.x/exceptions/
        raise Unauthorized("Parameter 'key' required.") #401
    
    #hash the key and check if it's authorized
    #see: https://werkzeug.palletsprojects.com/en/2.1.x/utils/#werkzeug.security.check_password_hash
    for psswd in passwords:
        from werkzeug.security import check_password_hash
        if check_password_hash(psswd, request_form["key"]):
            return True

    raise Unauthorized('Incorrect key.') #401

def check_for_event_format(request_form):
    from werkzeug.exceptions import BadRequest
    if not "data" in request_form:
        raise BadRequest("Parameter 'data' is required.") #400

def _repr_db(db):
    #avoid exposing internal database keys (that start with _)
    return {key:db[key] for key in db.keys() if not str(key).startswith("_") }

from flask_restx import Resource
from flask import request

@api.route('/log')
class Main(Resource):
    def post(self):
        check_for_access(request.form, db["_passwords"])
        check_for_event_format(request.form)
        
        db.append( request.form['data'] )

        return _repr_db(db)

    def get(self):
        check_for_access(request.form, db["_passwords"])

        return _repr_db(db)

if __name__ == '__main__':
    app.run(debug=_DEBUG)