"""
Authorization Handler module

Defines classes and exceptions related to authenticaiton for the app.

Missing_Username_Or_Password
Bad_Username_Or_Password
Custom exception classes

Authorization_Handler
The main class of this module. Exposes functions to authenticate users against
a Database.
"""

'''
TODO
enable support for digest authentication
this requires a plugin for Flask
    see:
    https://flask-httpauth.readthedocs.io/en/latest/
'''

class Missing_Username_Or_Password(Exception): pass
class Bad_Username_Or_Password(Exception): pass

class Authorization_Handler:
    """
    Authorization_Handler class

    A class that acts as middleware between the main Flask application and
    the Database.
    Checks for and verifies authentication information.
    """
    def __init__(self, database):
        self._db = database
        self._not_authorized_msg = "Incorrect username or password."
        self.not_authorized_msg = self._not_authorized_msg

    def _verify_authorization_present(self, request_authorization):
        """
        Given a dictionary from a Flask request (request.authorization)
        Determine if a username and password are present, and that they
        pass some basic criteria

        :return: the request.authorization dictionary on success
        raises otherwise
        """
        #example: {'username': 'peter', 'password': 'test'}

        if (request_authorization is None) or (len(request_authorization) == 0):
            raise Missing_Username_Or_Password("Username and password required.")

        if (len(request_authorization['username']) == 0) or \
        (len(request_authorization['password']) == 0):
            raise Bad_Username_Or_Password(self._not_authorized_msg)

        return request_authorization

    def is_authorized(self, request_authorization):
        """
        The main entrypoint for the class
        Takes a request.authorization dictionary and determines if the
        username and password contained therein is authorized; Otherwise raises

        :return: boolean, if authorized or not
        """
        self._verify_authorization_present(request_authorization)

        _u = request_authorization['username']
        _p = request_authorization['password']

        if not self._db.username_exists(_u):
            raise Bad_Username_Or_Password(self._not_authorized_msg)

        return self._db.username_has_password(_u, _p)