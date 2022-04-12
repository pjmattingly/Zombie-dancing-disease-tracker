"""
Validation and Standardization module

This module contains the logic to validate input; As well as raising helpful
errors back to the caller.

In addition, this module handles appending sensible defaults for optional
parameters of the input.
"""

'''
TODO
The validation portion of this module should be handled by Marshmallow
but our needs are so simple, at this time, that these simple functions should
suffice.
    see:
    https://marshmallow.readthedocs.io/en/stable/quickstart.html
'''

#see: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
class Malformed_Input(Exception): pass

def validate(row):
    """
    A function that acts as an entrypoint for the validation logic.

    :param row: dictionary
    """
    vns = Validation_and_Standardization()
    vns.validate(row)

def standardize(row):
    """
    A function that acts as an entrypoint for adding sensible defaults to
    the input.

    :param row: dictionary
    """

    vns = Validation_and_Standardization()
    return vns.standardize(row)

class Validation_and_Standardization:
    """
    A class that wraps the logic of validation, as well as the code to
    append sensible defaults to the input.
    """

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
        """
        A function that iterates over the various validation functions associated
        with the class. The functions raises a `Malformed_Input` exception
        when an issue occurs.

        :param row: dictionary
        """

        [func(row) for func in self._checks]

    def standardize(self, row):
        """
        A function that iterates over the various functions checking for optional
        parameters and adding defaults. The row is modified iteratively
        through each function call.

        :param row: dictionary
        :return: dictionary
        """

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
        """
        A function to check a row of input for the required keys needed for
        inserting a new row of data.

        :param row: dictionary
        :return: dictionary
        """

        _msg = self._error_msgs["_required_keys_check"]

        seen_keys = set( row.keys() )

        if not (set(self._required_keys) <= seen_keys):
            raise Malformed_Input(_msg)

        return row

    def _private_keys_check(self, row):
        """
        A function to check a row of input for keys that begin with an underscore
        and raising on finding them; As keys beginning with an underscore
        are reserved for internal use.

        :param row: dictionary
        """

        _msg = self._error_msgs["_private_keys_check"]
         
        if any( [str(k).startswith("_") for k in row.keys()] ):
            raise Malformed_Input(_msg)

    def _date_time_check(self, row):
        """
        A function to check for the "date_time" parameter in input, and appending
        a sensible default timestamp to the input if "date_time" is not present.

        :param row: dictionary
        :return: dictionary
        """

        #TODO, we should check if date_time is valid here, but this is very complex
        if (not "date_time" in list(row)):
            from datetime import datetime
            _row = dict(row)
            _row["date_time"] = datetime.now(tz=None)
            return _row

        return row

    def _notes_check(self, row):
        """
        A function to check for the "notes" parameter in input, and appending
        a sensible default value assocaited with a "notes" parameter
        if "notes" is not present.

        :param row: dictionary
        :return: dictionary
        """

        if (not "notes" in list(row)):
            _row = dict(row)
            _row["notes"] = None
            return _row
        return row

    def _add_timestamp(self, row):
        """
        A function to append a timestamp to each input.

        :param row: dictionary
        :return: dictionary
        """

        _row = dict(row)
        from datetime import datetime
        _row["_timestamp"] = datetime.now(tz=None)
        return _row