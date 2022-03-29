_DEBUG = True

from flask import Flask
app = Flask(__name__)

from flask_restx import Api
api = Api(app)

db = []

from flask_restx import Resource

@api.route('/log')
class Main(Resource):
    def post(self):
        from flask import request
        db.append( request.form['data'] )
        return db

    def get(self):
        return db

if __name__ == '__main__':
    app.run(debug=_DEBUG)