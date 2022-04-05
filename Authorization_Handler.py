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

        return self._db.username_has_password(_u, _p)