_DEBUG = True

from flask import Flask
app = Flask(__name__)

from flask_restx import Api
api = Api(app)

db = {}
db["passwords"] = []

def check_for_access(request_form, passwords):
    if not "key" in request_form:
        #instead of using the flask abort() use the internal exceptions
        #see: https://flask.palletsprojects.com/en/2.1.x/errorhandling/
        #https://werkzeug.palletsprojects.com/en/2.1.x/exceptions/
        from werkzeug.exceptions import Unauthorized
        raise Unauthorized("Parameter 'key' required.") #401
    
    #hash the key and check if it's authorized


from flask_restx import Resource
from flask import request

@api.route('/log')
class Main(Resource):
    def post(self):
        check_for_access(request.form, db["passwords"])
        
        db.append( request.form['data'] )

        return db

    def get(self):
        check_for_access(request.form, db["passwords"])

        return db

if __name__ == '__main__':
    app.run(debug=_DEBUG)