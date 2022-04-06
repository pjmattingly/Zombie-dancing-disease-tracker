def _parse_input():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('database_path', nargs='?', type=str)

    args = parser.parse_args()

    return {"database_path": args.database_path}

def _get_db_path(args):
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
    args = _parse_input()
    db_path = _get_db_path(args)

    from Database import Database as DB
    db = DB(db_path)

    return db

if __name__ == '__main__':
    db = init()

    #TEST
    _DEBUG = True
    db.add_user("test", "test")
    
    import Flask_app
    Flask_app.run(db, _DEBUG)