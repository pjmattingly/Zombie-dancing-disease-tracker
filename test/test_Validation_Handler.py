import pytest
import src.Validation_Handler

test_v = None

@pytest.fixture
def init():
    global test_v
    test_v = src.Validation_Handler.Validation_and_Standardization()

    yield

    del test_v
    test_v = None

class Test_zero_length_check:
    def test1(self, init):
        sample_row = {"data": ""}

        from src.Validation_Handler import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_v._zero_length_check( sample_row )

        assert test_v._error_msgs["_zero_length_check"] in str(excinfo.value)

    def test2(self, init):
        sample_row = {"": "some value"}

        from src.Validation_Handler import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_v._zero_length_check( sample_row )

        assert test_v._error_msgs["_zero_length_check"] in str(excinfo.value)

    def test3(self, init):
        sample_row = {"": ""}

        from src.Validation_Handler import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_v._zero_length_check( sample_row )

        assert test_v._error_msgs["_zero_length_check"] in str(excinfo.value)

class Test_required_keys_check:
    def test1(self, init):
        sample_row = {"some bad key": "some bad value"}

        from src.Validation_Handler import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_v._required_keys_check( sample_row )

        assert test_v._error_msgs["_required_keys_check"] in str(excinfo.value)

    def test2(self, init):
        #pick three random keys
        import random
        sample_row = {str(random.choice( test_v._required_keys )):"some value" for i in range(3)}

        from src.Validation_Handler import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_v._required_keys_check( sample_row )

        assert test_v._error_msgs["_required_keys_check"] in str(excinfo.value)

    def test3(self, init):
        sample_row = {str(k):"some value" for k in test_v._required_keys}

        test_v._required_keys_check( sample_row )

        assert True

class Test_date_time_check:
    def test1(self, init):
        sample_row = {"some key": "some value"}

        res = test_v._date_time_check(sample_row)

        assert "date_time" in list( res.keys() )

    def test2(self, init):
        sample_row = {"date_time": "some timestamp"}

        res = test_v._date_time_check(sample_row)

        assert "some timestamp" in list( res.values() )

class Test_notes_check:
    def test1(self, init):
        sample_row = {"some key": "some value"}

        res = test_v._notes_check(sample_row)

        assert "notes" in list( res.keys() )
    
    def test2(self, init):
        sample_row = {"notes": "some value"}

        res = test_v._notes_check(sample_row)

        assert "some value" in list( res.values() )

class Test_validate1:
    def test1(self, init):
        sample_row = {"data": ""}

        from src.Validation_Handler import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_v.validate( sample_row )

        assert test_v._error_msgs["_zero_length_check"] in str(excinfo.value)

    def test2(self, init):
        sample_row = {"some bad key": "some bad value"}

        from src.Validation_Handler import Malformed_Input
        with pytest.raises(Malformed_Input) as excinfo:
            test_v.validate( sample_row )

        assert test_v._error_msgs["_required_keys_check"] in str(excinfo.value)

    def test3(self, init):
        sample_row = {str(k):"some value" for k in test_v._required_keys}

        test_v.validate(sample_row)

        assert True

class Test_validate2:
    def test1(self, init):
        from src.Validation_Handler import validate

        sample_row = {str(k):"some value" for k in test_v._required_keys}

        test_v.validate(sample_row)

        assert True

class Test_standardize1:
    def test1(self, init):
        sample_row = {str(k):"some value" for k in test_v._required_keys}

        res = test_v.standardize(sample_row)

        assert "date_time" in list( res.keys() )
        assert "notes" in list( res.keys() )

class Test_standardize2:
    def test1(self, init):
        from src.Validation_Handler import standardize

        sample_row = {str(k):"some value" for k in test_v._required_keys}

        res = test_v.standardize(sample_row)

        assert "date_time" in list( res.keys() )
        assert "notes" in list( res.keys() )