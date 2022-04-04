import pytest
from unittest.mock import patch
from app import Main

from flask import Flask
_app = Flask(__name__)

class Test_get:
    def test_request_too_large(self, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        with _app.test_request_context(
            "/log", method="GET", data={}, content_length=(2 * 1024 + 1)
        ):
            from werkzeug.exceptions import RequestURITooLarge
            with pytest.raises(RequestURITooLarge) as excinfo:
                Main.get(mock_self)

    def test_no_password(self):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        with _app.test_request_context(
            "/log", method="GET", data={}
        ):
            from werkzeug.exceptions import BadRequest
            with pytest.raises(BadRequest) as excinfo:
                Main.get(mock_self)

            assert "Required argument" in str(excinfo.value)

    def test_typo_for_password(self):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        with _app.test_request_context(
            "/log", method="GET", data={"ky": "some password"}
        ):
            from werkzeug.exceptions import BadRequest
            with pytest.raises(BadRequest) as excinfo:
                Main.get(mock_self)

            assert "Required argument" in str(excinfo.value)

    def test_bad_password(self, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return False

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        with _app.test_request_context(
            "/log", method="GET", data={"key": "some bad password"}
        ):
            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.get(mock_self)

            assert "Incorrect key" in str(excinfo.value)

    from app import Database
    @patch.object(Database, '__repr__')
    def test_no_search(self, mock_method, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return True

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        with _app.test_request_context(
            "/log", method="GET", data={"key": "test"}
        ):
            Main.get(mock_self)

        mock_method.assert_called() #called __repr__()

    from app import Database
    @patch.object(Database, 'search')
    def test_search(self, mock_method, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return True

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        with _app.test_request_context(
            "/log", method="GET", data={"key": "test", "some key": "some data"}
        ):
            Main.get(mock_self)

        #called search()
        mock_method.assert_called_with({"some key": "some data"})

class Test_post:
    def test_request_too_large(self, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        _size = (2 * 1024 * 1024 * 1024 + 1)
        with _app.test_request_context(
            "/log", method="POST", data={}, content_length=_size
        ):
            from werkzeug.exceptions import RequestURITooLarge
            with pytest.raises(RequestURITooLarge) as excinfo:
                Main.post(mock_self)

    def test_no_password(self):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        with _app.test_request_context(
            "/log", method="POST", data={}
        ):
            from werkzeug.exceptions import BadRequest
            with pytest.raises(BadRequest) as excinfo:
                Main.post(mock_self)

            assert "Required argument" in str(excinfo.value)

    def test_bad_password(self, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return False

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        with _app.test_request_context(
            "/log", method="POST", data={"key": "some bad password"}
        ):
            from werkzeug.exceptions import Unauthorized
            with pytest.raises(Unauthorized) as excinfo:
                Main.post(mock_self)

            assert "Incorrect key" in str(excinfo.value)

    from app import Database
    @patch.object(Database, 'append')
    @patch.object(Database, '__repr__')
    def test_good_append(self, mock_repr, mock_append, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return True

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        with _app.test_request_context(
            "/log", method="GET", data={"key": "test", "some key": "some data"}
        ):
            Main.post(mock_self)

        mock_append.assert_called()
        mock_repr.assert_called()
        called_with = mock_append.call_args.args[0]
        assert "some key" in called_with
        assert "some data" in called_with["some key"]

    from app import Database
    @patch.object(Database, 'append')
    def test_out_of_space(self, mock_append, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return True

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        import errno
        mock_append.side_effect = OSError(errno.ENOSPC)

        with _app.test_request_context(
            "/log", method="GET", data={"key": "test", "some key": "some data"}
        ):
            from app import InsufficientStorage
            with pytest.raises(InsufficientStorage) as excinfo:
                Main.post(mock_self)

    from app import Database
    @patch.object(Database, 'append')
    def test_other_OSError(self, mock_append, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return True

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        mock_append.side_effect = OSError(0)

        with _app.test_request_context(
            "/log", method="GET", data={"key": "test", "some key": "some data"}
        ):
            with pytest.raises(OSError) as excinfo:
                Main.post(mock_self)

        assert str(0) in str(excinfo.value)

    from app import Database
    @patch.object(Database, 'append')
    def test_other_error(self, mock_append, monkeypatch):
        from unittest.mock import MagicMock
        mock_self = MagicMock()

        def mock_check_password(self, password):
            return True

        from app import Database
        monkeypatch.setattr(Database, "check_password", mock_check_password)

        class Mock_Exception(Exception): pass
        mock_append.side_effect = Mock_Exception()

        with _app.test_request_context(
            "/log", method="GET", data={"key": "test", "some key": "some data"}
        ):
            with pytest.raises(Mock_Exception) as excinfo:
                Main.post(mock_self)