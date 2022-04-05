import pytest

from Database import Database
from Database import Bad_Username_Or_Password

test_db = None

@pytest.fixture
def setup_database(tmp_path):
    global test_db
    test_db = Database(tmp_path)

    yield

    test_db = None

class Test__init__:
    def test1(self, setup_database):
        try:
            Database("some bad path")
            assert False
        except OSError:
            assert True

    def test2(self, setup_database, tmp_path):
        Database(tmp_path)
        assert True

class Test_add_user:
    def test1(self, setup_database):
        user_records = test_db._user_table.all()

        assert len(user_records) == 0

        test_db.add_user("test", "test")

        user_records = test_db._user_table.all()

        assert len(user_records) == 1

    def test2(self, setup_database):
        from Database import Bad_Username_Or_Password
        with pytest.raises(Bad_Username_Or_Password) as excinfo:
            test_db.add_user("", "test")

    def test3(self, setup_database):
        from Database import Bad_Username_Or_Password
        with pytest.raises(Bad_Username_Or_Password) as excinfo:
            test_db.add_user("test", "")

    def test4(self, setup_database):
        from Database import Bad_Username_Or_Password
        with pytest.raises(Bad_Username_Or_Password) as excinfo:
            test_db.add_user("", "")

class Test_username_exists:
    def test1(self, setup_database):
        test_db.add_user("test", "test")

        assert test_db._username_exists("test")

    def test2(self, setup_database):
        test_db.add_user("test", "test")

        assert not test_db._username_exists("some other username")

class Test_username_has_password:
    def test1(self, setup_database):
        test_db.add_user("test", "test")

        assert test_db.username_has_password("test", "test")

    def test2(self, setup_database):
        test_db.add_user("test", "test")

        assert not test_db.username_has_password("test", "some bad password")

    def test3(self, setup_database):
        test_db.add_user("test", "test")

        from Database import No_Such_User
        with pytest.raises(No_Such_User) as excinfo:
            test_db.username_has_password(
                "some bad username", "some bad password"
            )

class Test_append:
    def test1(self, setup_database):
        res = test_db.__repr__()

        assert len(res) == 0

        sample_row = {"data": "some stored data"}
        res = test_db.append( sample_row )

        assert len(res) == 1
        assert "data" in res[0]
        assert res[0]["data"] == "some stored data"

    def test2(self, setup_database):
        sample_row = {"data": "some stored data 1"}
        res = test_db.append( sample_row )

        import time
        time.sleep(.1) #add a small delay to make sure timestamps are unique

        sample_row = {"data": "some stored data 2"}
        res = test_db.append( sample_row )

        assert all( ["_timestamp" in row for row in res] )

        set_timestamps = {row["_timestamp"] for row in res}

        assert len(set_timestamps) == 2 #all unique timestamps

    def test3(self, setup_database):
        sample_row = {"data": ""}

        from Database import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_db.append( sample_row )

class Test_escape_input:
    def test1(self, setup_database):
        sample_row = {"data": "some stored data"}
        res = test_db._escape_input( sample_row )

        assert len(res) == 1
        assert "data" in res
        assert res["data"] == "some stored data"

    def test2(self, setup_database):
        sample_row = {"data": "<b>some stored data<\b>"}
        res = test_db._escape_input( sample_row )

        assert len(res) == 1
        assert "data" in res
        assert "some stored data" in res["data"]
        assert '&lt;b&gt;' in res["data"] #<b>
        assert '&lt;\x08&gt;' in res["data"] #<\b>

    def test3(self, setup_database):
        sample_row = {"<b>data<\b>": "some stored data"}
        res = test_db._escape_input( sample_row )

        assert len(res) == 1
        k = list(res.keys())[0]
        assert "data" in k
        assert '&lt;b&gt;' in k #<b>
        assert '&lt;\x08&gt;' in k #<\b>

class Test_validate_input:
    def test1(self, setup_database):
        sample_row = {"data": ""}

        from Database import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_db._validate_input( sample_row )

    def test2(self, setup_database):
        sample_row = {"": "some value"}

        from Database import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_db._validate_input( sample_row )

    def test3(self, setup_database):
        sample_row = {"": ""}

        from Database import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_db._validate_input( sample_row )

class Test_search:
    def test1(self, setup_database):
        res = test_db.search({})

        assert len(res) == 0

    def test2(self, setup_database):
        res = test_db.search({"some key": "some data"})

        assert len(res) == 0

    def test3(self, setup_database):
        sample_row = {"data": "some stored data"}
        test_db.append( sample_row )

        res = test_db.search({"data": "some bad data"})

        assert len(res) == 0

    def test4(self, setup_database):
        sample_row = {"data": "some stored data"}
        test_db.append( sample_row )

        res = test_db.search({"some bad key": "some stored data"})

        assert len(res) == 0

    def test5(self, setup_database):
        sample_row = {"data": "some stored data"}
        test_db.append( sample_row )

        res = test_db.search({"data": "some stored data"})

        assert len(res) == 1
        assert "data" in res[0]
        assert res[0]["data"] == "some stored data"

    def test6(self, setup_database):
        sample_row = {"data": "some stored data"}
        test_db.append( sample_row )

        res = test_db.search({"data": ""})

        assert len(res) == 0

    def test7(self, setup_database):
        sample_row = {"data": "some stored data"}
        test_db.append( sample_row )

        res = test_db.search({"": "some stored data"})

        assert len(res) == 0

    def test8(self, setup_database):
        sample_row = {"data": "some stored data"}
        test_db.append( sample_row )

        res = test_db.search({"": ""})

        assert len(res) == 0

from unittest.mock import patch
class Test_check_disk_usage:
    @patch('shutil.disk_usage')
    def test1(self, mock_disk_usage, setup_database):
        from unittest.mock import MagicMock
        test_res = MagicMock()
        mock_disk_usage.return_value = test_res
        test_res.free = 1
        test_res.total = 1

        res = test_db._check_disk_usage()
        
        assert True

    @patch('shutil.disk_usage')
    def test2(self, mock_disk_usage, setup_database):
        from unittest.mock import MagicMock
        test_res = MagicMock()
        mock_disk_usage.return_value = test_res
        test_res.free = 0
        test_res.total = 1

        try:
            test_db._check_disk_usage()
        except OSError as e:
            import errno
            assert e.errno == errno.ENOSPC
        else:
            assert False

    @patch('shutil.disk_usage')
    def test3(self, mock_disk_usage, setup_database):
        from unittest.mock import MagicMock
        test_res = MagicMock()
        mock_disk_usage.return_value = test_res
        test_res.free = 0
        test_res.total = 1

        try:
            test_db.append({"test", "test"})
        except OSError as e:
            import errno
            assert e.errno == errno.ENOSPC
        else:
            assert False

class Test__repr__:
    def test1(self, setup_database):
        res = test_db.__repr__()

        assert isinstance(res, list)
        assert len(res) == 0

    def test2(self, setup_database):
        sample_row = {"data": "some stored data 1"}
        res = test_db.append( sample_row )

        import time
        time.sleep(.1) #add a small delay to make sure timestamps are unique

        sample_row = {"data": "some stored data 2"}
        res = test_db.append( sample_row )

        assert res[0]["_timestamp"] < res[1]["_timestamp"]

class Test_to_JSON_safe:
    def test1(self, setup_database):
        sample_row = {"data": "some stored data 1"}
        res1 = test_db.append( sample_row )

        res2 = test_db.__repr__()

        with pytest.raises(TypeError) as excinfo:
            import json
            json.dumps(res2)

        from Database import to_JSON_safe
        res3 = to_JSON_safe(res2)

        import json
        json.dumps(res3)

        assert True