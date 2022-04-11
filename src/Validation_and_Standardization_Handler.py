'''
TODO
The validation portion of this module should be handled by Marshmallow
but our needs are so simple at this time, that these simple functions should
suffice.
    see:
    https://marshmallow.readthedocs.io/en/stable/quickstart.html
'''
#see: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
class Malformed_Input(Exception): pass

def validate(row):
    vns = Validation_and_Standardization()
    vns.validate(row)

def standardize(row):
    vns = Validation_and_Standardization()
    return vns.standardize(row)

class Validation_and_Standardization:
    def __init__(self):
        self._checks = [self._zero_length_check, self._required_keys_check]
        self._mods = [
            self._date_time_check,
            self._notes_check,
            self._add_timestamp
        ]

        self._required_keys = ["doctor", "patient", "event_type", "location"]

        self._error_msgs = {
        "_zero_length_check":"All keys and values should have non-zero length.",
        "_required_keys_check":
        f"The following keys are required for each event: {self._required_keys}",
        "_private_keys_check" : f"Keys should not being with underscore: '_' ",
        }

    def validate(self, row):
        [func(row) for func in self._checks]

    def standardize(self, row):
        _row = row
        for func in self._mods:
            _row = func(_row)

        return _row

    def _zero_length_check(self, row):
        """
        A function to validate the data in a new row; Raising on empty strings
        for either key or value.

        :param row: dictionary
        :return: dictionary
        """

        _msg = self._error_msgs["_zero_length_check"]
        
        for k in row.keys():
            if len(k) == 0:
                raise Malformed_Input(_msg)
            if len(row[k]) == 0:
                raise Malformed_Input(_msg)

        return row

    def _required_keys_check(self, row):
        _msg = self._error_msgs["_required_keys_check"]

        seen_keys = set( row.keys() )

        if not (set(self._required_keys) <= seen_keys):
            raise Malformed_Input(_msg)

        return row

    def _private_keys_check(self, row):
        _msg = self._error_msgs["_private_keys_check"]
         
        if any( [str(k).startswith("_") for k in row.keys()] ):
            raise Malformed_Input(_msg)

    def _date_time_check(self, row):
        #TODO, we should check if date_time is valid here, but this is very complex
        if (not "date_time" in list(row)):
            from datetime import datetime
            _row = dict(row)
            _row["date_time"] = datetime.now(tz=None)
            return _row

        return row

    def _notes_check(self, row):
        if (not "notes" in list(row)):
            _row = dict(row)
            _row["notes"] = None
            return _row
        return row

    def _add_timestamp(self, row):
        _row = dict(row)
        from datetime import datetime
        _row["_timestamp"] = datetime.now(tz=None)
        return _row