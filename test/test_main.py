import pytest
import main

class Test_init:
    from unittest.mock import patch
    @patch.object(main, '_get_db_path')
    def test_1(self, mock_db_path, tmp_path):
        mock_db_path.return_value = tmp_path

        main.init()

        tmp_dir_content = list( tmp_path.iterdir() )

        assert len(tmp_dir_content) == 1
        assert "db.json" in tmp_dir_content[0].name

class Test_parse_input:
    #note, patching argv in this way causes argparse to return an empty list
    from unittest.mock import patch
    import sys
    @patch.object(sys, 'argv')
    def test_1(self, mock_argv):
        res = main._parse_input()

        assert len(res['database_path']) == 0

class Test_get_db_path:
    def test_1(self):
        mock_args = {"database_path": None}

        res = main._get_db_path(mock_args)

        from pathlib import Path
        assert Path(res).exists()
    
    def test_2(self):
        mock_args = {"database_path": "some bad path"}

        with pytest.raises(OSError) as excinfo:
            main._get_db_path(mock_args)

        assert "not found" in str(excinfo.value)

    def test_3(self, tmp_path):
        mock_args = {"database_path": tmp_path}

        res = main._get_db_path(mock_args)

        assert res == tmp_path