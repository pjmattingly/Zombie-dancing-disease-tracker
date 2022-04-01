import pytest

from app import Database

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

class Test_add_password:
    def test1(self, setup_database):
        res = test_db.get_passwords()

        assert len(res) == 0

        test_db.add_password("test")

        res = test_db.get_passwords()

        assert len(res) == 1

class Test_create_password:
    def test1(self, setup_database):
        res = test_db._create_password("test")

        assert isinstance(res, str)

class Test_get_passwords:
    def test1(self, setup_database):
        test_db.add_password("test")
        res = test_db._get_passwords()

        assert isinstance(res, list)
        assert len(res) == 1

class Test_check_password:
    def test1(self, setup_database):
        test_db.add_password("test")
        res = test_db._check_password("some fake password", test_db._get_passwords())

        assert res == False

    def test2(self, setup_database):
        test_db.add_password("test")
        res = test_db._check_password("test", test_db._get_passwords())

        assert res == True

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

        sample_row = {"data": "some stored data 2"}
        res = test_db.append( sample_row )

        assert all( ["_timestamp" in row for row in res] )

        set_timestamps = {row["_timestamp"] for row in res}

        assert len(set_timestamps) == 2 #all unique timestamps

class Test__repr__:
    def test1(self, setup_database):
        res = test_db.__repr__()

        assert isinstance(res, list)
        assert len(res) == 0

    def test2(self, setup_database):
        sample_row = {"data": "some stored data 1"}
        res = test_db.append( sample_row )

        sample_row = {"data": "some stored data 2"}
        res = test_db.append( sample_row )

        assert res[0]["_timestamp"] < res[1]["_timestamp"]

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

class Test_search:
    def test1(self, setup_database):
        #sample_row = {"data": "some stored data"}
        #res = test_db.append( sample_row )

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