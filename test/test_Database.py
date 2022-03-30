import pytest

from app import Database

test_db = None

@pytest.fixture
def setup_database():
    global test_db
    test_db = Database()

    yield

    test_db = None

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

        assert "data" in res
        assert len(res["data"]) == 0

        sample_row = [{"key": "some password", "data": "some stored data"}]
        res = test_db.append( sample_row )

        assert len(res) == 1

        assert len(test_db.__repr__()["data"]) == 1

class Test__repr__:
    def test1(self, setup_database):
        res = test_db.__repr__()

        assert isinstance(res, dict)
        assert "data" in res
        assert len(res) == 1