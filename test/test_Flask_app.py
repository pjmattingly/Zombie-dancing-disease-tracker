import pytest
from unittest.mock import patch
from Flask_app import Main

from flask import Flask
_app = Flask(__name__)

test_db = None

@pytest.fixture
def setup_database(tmp_path):
    from Database import Database
    global test_db
    test_db = Database(tmp_path)

def teardown_database():
    global test_db
    test_db = None

@pytest.fixture
def setup_flask_app(setup_database):
    import Flask_app as fa
    fa._db = test_db

    from Authorization_Handler import Authorization_Handler
    fa._ah = Authorization_Handler(fa._db)

    yield

    teardown_database()

class Test_post:
    def test_request_too_large(self, setup_flask_app, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        _size = (2 * 1024 * 1024 * 1024 + 1)
        with _app.test_request_context(
            "/log", method="POST", data={}, content_length=_size
        ):
            from werkzeug.exceptions import RequestURITooLarge
            with pytest.raises(RequestURITooLarge) as excinfo:
                Main.post(mock_self)

    def test_no_password(self, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        with _app.test_request_context(
            "/log", method="POST", data={}
        ):
            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.post(mock_self)

            assert "required" in str(excinfo.value)

    #DEBUG
    #def test_DEBUG(self):
    #    pytest.exit("DEBUG")

    def test_bad_password(self, setup_flask_app, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            from Authorization_Handler import Bad_Username_Or_Password
            raise Bad_Username_Or_Password()

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="POST", data={}
        ):
            from flask import request
            request.authorization = {"test": "test"}

            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.post(mock_self)

            assert "Incorrect" in str(excinfo.value)

    def test_wrong_password(self, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return False

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="POST", data={}
        ):
            from flask import request
            request.authorization = {'username' : "test", 'password' : "test"}

            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.post(mock_self)

            assert "Incorrect" in str(excinfo.value)

    from Database import Database
    @patch.object(Database, 'append')
    @patch.object(Database, '__repr__')
    def test_good_append(self, mock_repr, mock_append, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return True

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="POST", data={"some key": "some data"}
        ):
            from flask import request
            request.authorization = {'username' : "test", 'password' : "test"}

            Main.post(mock_self)

        mock_append.assert_called()
        mock_repr.assert_called()
        called_with = mock_append.call_args.args[0]
        assert "some key" in called_with
        assert "some data" in called_with["some key"]

    from Database import Database
    @patch.object(Database, 'append')
    @patch.object(Database, '__repr__')
    def test_no_data(self, mock_repr, mock_append, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return True

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="POST", data={}
        ):
            from flask import request
            request.authorization = {'username' : "test", 'password' : "test"}

            res = Main.post(mock_self)

        mock_append.assert_not_called()
        mock_repr.assert_called()
        assert len(res) == 0

    from Database import Database
    @patch.object(Database, 'append')
    def test_out_of_space(self, mock_append, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return True

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        import errno
        mock_append.side_effect = OSError(errno.ENOSPC)

        with _app.test_request_context(
            "/log", method="POST", data={"some key": "some data"}
        ):
            from flask import request
            request.authorization = {'username' : "test", 'password' : "test"}

            from Flask_app import InsufficientStorage
            with pytest.raises(InsufficientStorage) as excinfo:
                Main.post(mock_self)

    from Database import Database
    @patch.object(Database, 'append')
    def test_other_OSError(self, mock_append, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return True

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        mock_append.side_effect = OSError(0)

        with _app.test_request_context(
            "/log", method="POST", data={"some key": "some data"}
        ):
            from flask import request
            request.authorization = {'username' : "test", 'password' : "test"}

            with pytest.raises(OSError) as excinfo:
                Main.post(mock_self)

        assert str(0) in str(excinfo.value)

    from Database import Database
    @patch.object(Database, 'append')
    def test_other_error(self, mock_append, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return True

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        class Mock_Exception(Exception): pass
        mock_append.side_effect = Mock_Exception()

        with _app.test_request_context(
            "/log", method="POST", data={"some key": "some data"}
        ):
            from flask import request
            request.authorization = {'username' : "test", 'password' : "test"}

            with pytest.raises(Mock_Exception) as excinfo:
                Main.post(mock_self)

class Test_get:
    def test_request_too_large(self, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        with _app.test_request_context(
            "/log", method="GET", data={}, content_length=(2 * 1024 + 1)
        ):
            from werkzeug.exceptions import RequestURITooLarge
            with pytest.raises(RequestURITooLarge) as excinfo:
                Main.get(mock_self)

    def test_no_password(self, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        with _app.test_request_context(
            "/log", method="GET", data={}
        ):
            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.get(mock_self)

            assert "required" in str(excinfo.value)

    def test_bad_password(self, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            from Authorization_Handler import Bad_Username_Or_Password
            raise Bad_Username_Or_Password()

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="GET", data={}
        ):
            from flask import request
            request.authorization = {"test": "test"}

            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.get(mock_self)

            assert "Incorrect" in str(excinfo.value)

    def test_wrong_password(self, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return False

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="GET", data={}
        ):
            from flask import request
            request.authorization = {'username' : "test", 'password' : "test"}

            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.get(mock_self)

            assert "Incorrect" in str(excinfo.value)

    from Database import Database
    @patch.object(Database, '__repr__')
    def test_no_search(self, mock_repr, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return True

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="GET", data={}
        ):
            Main.get(mock_self)

        mock_repr.assert_called()

    from Database import Database
    @patch.object(Database, 'search')
    def test_search(self, mock_search, monkeypatch, setup_flask_app):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_is_authorized(self, request_authorization):
            return True

        from Authorization_Handler import Authorization_Handler
        monkeypatch.setattr(
            Authorization_Handler, "is_authorized", mock_is_authorized
            )

        with _app.test_request_context(
            "/log", method="GET", data={"some key": "some data"}
        ):
            Main.get(mock_self)

        mock_search.assert_called_with({"some key": "some data"})

class Test_run:
    def test_1(self, setup_database):
        from unittest.mock import MagicMock
        import Flask_app
        Flask_app._app = MagicMock()

        from Flask_app import run
        run(test_db)

        assert not Flask_app._db is None
        assert not Flask_app._ah is None

        Flask_app._app.run.assert_called()

        teardown_database()