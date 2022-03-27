import os
os.environ['FLASK_ENV'] = "development" #FLASK_ENV=development

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run()  # run our Flask app