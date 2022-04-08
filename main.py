"""
An audit log service, built on flask.

usage: main.py [-h] [database_path]

positional arguments:
  database_path

optional arguments:
  -h, --help     show this help message and exit

:param database_path: A path indicating where to save the database file.
                    Defaults to the current directory

----

Client usage:

To list the content of the database:

curl <URL of server>:5000/log --user username:password -X GET

To add data to the database:

curl <URL of server>:5000/log --user username:password --data "<key>=<value>" -X POST

To search the database for records containing <key> -> <value>

curl <URL of server>:5000/log --user username:password --data "<key>=<value>" -X GET
"""

def _parse_input():
    """
    Contains the logic for parsing command-line input and returns a dictionary
    of possible command-line options and their values.

    :return: A dictionary mapping command line options to their or None
    """
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('database_path', nargs='?', type=str)

    args = parser.parse_args()

    return {"database_path": args.database_path}

def _get_db_path(args):
    """
    Given a dictionary of args from _parse_input() determine if the args
    parameter contains a valid path to save the database file to; Raising if
    the path isn't valid.

    :param args: A dictionary of args as returned by _parse_input()
    :return: a Path object of a valid path to save the file created by Database
    """
    from pathlib import Path
    db_path = Path.cwd()

    if not args["database_path"] is None:
        from pathlib import Path
        _path = Path(args["database_path"])

        if not _path.exists():
            raise OSError(f"Path not found: {_path}")

        db_path = _path.resolve()

    return db_path

def init():
    """
    Parses command-line input and then initializes an instance of Database
    with a valid path so it can save its data-file.

    :return: an initialized Database object
    """
    args = _parse_input()
    db_path = _get_db_path(args)

    from Database import Database as DB
    db = DB(db_path)

    return db

if __name__ == '__main__':
    db = init()

    #TEST
    #_DEBUG = True
    #db.add_user("test", "test")
    
    import Flask_app
    #Flask_app.run(db, _DEBUG)
    Flask_app.run(db)