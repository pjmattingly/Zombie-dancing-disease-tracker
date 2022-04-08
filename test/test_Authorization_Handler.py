import pytest
from Database import Database
from Authorization_Handler import Authorization_Handler

test_ah = None
test_db = None

@pytest.fixture
def setup_auth_handler(tmp_path):
    global test_db
    test_db = Database(tmp_path)

    global test_ah
    test_ah = Authorization_Handler(test_db)

    yield

    test_db = None
    test_ah = None

class Test_verify_authorization_present:
    #test_input = {'username': 'test', 'password': 'test'}
    
    def test1(self, setup_auth_handler):
        test_input = None

        from Authorization_Handler import Missing_Username_Or_Password
        with pytest.raises(Missing_Username_Or_Password) as excinfo:
            test_ah._verify_authorization_present(test_input)

    def test2(self, setup_auth_handler):
        test_input = {}

        from Authorization_Handler import Missing_Username_Or_Password
        with pytest.raises(Missing_Username_Or_Password) as excinfo:
            test_ah._verify_authorization_present(test_input)

    def test3(self, setup_auth_handler):
        test_input = {'username': '', 'password': 'test'}

        from Authorization_Handler import Bad_Username_Or_Password
        with pytest.raises(Bad_Username_Or_Password) as excinfo:
            test_ah._verify_authorization_present(test_input)

    def test4(self, setup_auth_handler):
        test_input = {'username': 'test', 'password': ''}

        from Authorization_Handler import Bad_Username_Or_Password
        with pytest.raises(Bad_Username_Or_Password) as excinfo:
            test_ah._verify_authorization_present(test_input)

    def test5(self, setup_auth_handler):
        test_input = {'username': '', 'password': ''}

        from Authorization_Handler import Bad_Username_Or_Password
        with pytest.raises(Bad_Username_Or_Password) as excinfo:
            test_ah._verify_authorization_present(test_input)

    def test6(self, setup_auth_handler):
        test_input = {'username': 'test', 'password': 'test'}

        test_ah._verify_authorization_present(test_input)
        
        assert True

class Test_is_authorized:
    #test_input = {'username': 'test', 'password': 'test'}
    
    def test1(self, setup_auth_handler):
        test_input = {'username': 'test', 'password': 'test'}
        test_db.add_user('test', 'test')

        assert test_ah.is_authorized(test_input)

    def test2(self, setup_auth_handler):
        test_input = {'username': 'test', 'password': 'some bad password'}
        test_db.add_user('test', 'test')

        assert not test_ah.is_authorized(test_input)

    def test3(self, setup_auth_handler):
        test_input = {'username': 'some bad username', 'password': 'test'}
        test_db.add_user('test', 'test')

        from Authorization_Handler import Bad_Username_Or_Password
        with pytest.raises(Bad_Username_Or_Password) as excinfo:
            test_ah.is_authorized(test_input)