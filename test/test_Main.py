import pytest
from unittest.mock import patch
from app import Main

from flask import Flask
_app = Flask(__name__)

class Test_get:
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
            from werkzeug.exceptions import BadRequest
            with pytest.raises(BadRequest) as excinfo:
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