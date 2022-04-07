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

'''
TODO
    if we need to support larger upload/POST sizes for logs we can implement
    support for file uploading, as an alternative to using POST
    or we can make more elaborate use of the --form option
        see: https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/
'''

'''
BUG
    Requests without a valid content_length causes curl to hang; likely due
    to an issue with Flask or Werkzeug
        see:
        https://github.com/pallets/flask/issues/1289
    avoid using --ignore-content-length with curl
'''
'''
TODO
    HTTPS
    It would be best if the over-the-wire content was encrypted
    there seems to be ways of making Flask do HTTPS, but they seem to be poorly
    documented
        see:
        https://stackoverflow.com/questions/29458548/can-you-add-https-functionality-to-a-python-flask-web-server
        https://medium.com/@timetraveller_x/setting-up-ssl-on-iis-with-python-flask-8d21847a3594
        https://stackoverflow.com/questions/49678561/enable-https-on-werkzeug-using-key-cert-as-strings
    So we may want to switch to a different router/framework/web server
    with better support for HTTPS
        e.g., https://docs.djangoproject.com/en/4.0/topics/security/
    Then also HTTPs for cURL seemed to be more difficult than was warranted for
    this exercise
        see:
        https://stackoverflow.com/questions/10079707/https-connection-using-curl-from-command-line
'''
'''
TODO
    JSON
    Adding JSON support seems trivial, but seemed to more complex than
    was arranted for this exercise
    It would be useful to have the server accept JSON input as well as
    plain-text
        see:
        https://flask.palletsprojects.com/en/2.1.x/api/#module-flask.json
'''
_db = None
_ah = None

def run(db, _debug = False):
    global _ah
    global _db

    _db = db

    from Authorization_Handler import Authorization_Handler
    _ah = Authorization_Handler(db)

    _app.run(debug=_debug)

from flask import Flask
_app = Flask(__name__)

from flask_restx import Api
_api = Api(_app)

#rate limiting to avoid swamping the server
from flask_limiter import Limiter
_limiter = Limiter(
    _app,
    #apply the limit to all incoming requests not just single IPs
    key_func = lambda : "",
    )

#custom exception for HTTP error 507
from werkzeug.exceptions import HTTPException
class InsufficientStorage(HTTPException):
    code = 507
    description = 'Insufficient Storage'

from flask_restx import Resource
@_api.route('/log')
class Main(Resource):
    #apply the rate limiter to each handler
    #see: https://flask-limiter.readthedocs.io/en/stable/recipes.html#using-flask-pluggable-views
    decorators = [_limiter.limit("20/second")]

    def post(self):
        from flask import request
        from flask import abort

        #limit POST requests to ~2GB
        #see: https://stackoverflow.com/questions/2880722/can-http-post-be-limitless
        #see: https://serverfault.com/questions/151090/is-there-a-maximum-size-for-content-of-an-http-post
        if not request.content_length is None:
            if request.content_length > 2 * 1024 * 1024 * 1024:
                #see: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.15
                abort(414)

        from Authorization_Handler import Missing_Username_Or_Password
        from Authorization_Handler import Bad_Username_Or_Password
        try:
            authorized = _ah.is_authorized( request.authorization )
        except Missing_Username_Or_Password:
            abort(401, "Username and password required.")
        except Bad_Username_Or_Password:
            abort(401, _ah.not_authorized_msg)
        else:
            if not authorized:
                abort(401, _ah.not_authorized_msg)
        
        _input = dict(request.form)
        
        if len(_input) == 0: #don't append empty input
            from Database import to_JSON_safe
            return to_JSON_safe( _db.__repr__() )

        _input["_user"] = request.authorization['username']

        try:
            res = _db.append( _input )
        except OSError as e:
            import errno
            if ( str(errno.ENOSPC) == str(e) ):
                m = 'Could not append to the database as out of storage.'
                raise InsufficientStorage(m)
            else:
                raise #raise other OSError

        from Database import to_JSON_safe
        return to_JSON_safe( _db.__repr__() )

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

        from Authorization_Handler import Missing_Username_Or_Password
        from Authorization_Handler import Bad_Username_Or_Password
        try:
            authorized = _ah.is_authorized( request.authorization )
        except Missing_Username_Or_Password:
            abort(401, "Username and password required.")
        except Bad_Username_Or_Password:
            abort(401, _ah.not_authorized_msg)
        else:
            if not authorized:
                abort(401, _ah.not_authorized_msg)

        search_args = dict(request.form)

        #if no query, then return the entire database
        if len(search_args) == 0:
            from Database import to_JSON_safe
            return to_JSON_safe( _db.__repr__() )

        from Database import to_JSON_safe
        return to_JSON_safe( _db.search(search_args) )