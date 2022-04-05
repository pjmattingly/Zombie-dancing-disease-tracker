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

        if (len(request_authorization['username']) == 0) or \
        (len(request_authorization['password']) == 0):
            raise Bad_Username_Or_Password(self._not_authorized_msg)

        return request_authorization

    def is_authorized(self, request_authorization):
        self._verify_authorization_present(request_authorization)

        _u = request_authorization['username']
        _p = request_authorization['password']

        return self._db.username_has_password(_u, _p)