import pytest

from xprocess import ProcessStarter
#handles starting up the server in the background and ensuring cleanup
#and termination post-testing
#see: https://github.com/pytest-dev/pytest-xprocess

@pytest.fixture
def setup_server(xprocess, tmp_path):
    #TODO
    #replace these `raise`s with proper exceptions

    from pathlib import Path
    app_path = Path.cwd() / "main.py"

    if not app_path.exists():
        raise #can't find main entry point for testing

    import shutil
    python_path = shutil.which("python")

    if python_path is None:
        raise #can't find Python

    class Starter(ProcessStarter):
        pattern = "" #required for Starter to be instantiated
        
        timeout = 5 #wait for the process to start ~5 seconds

        # command to start process
        args = [ python_path, str(app_path), str(tmp_path.resolve()) ]

        terminate_on_interrupt = True

        def startup_check(self):
            res = run_curl("--user test:test -X GET")

            first_check = isinstance(res, list)
            second_check = (len(res) == 0)

            return (first_check and second_check)

    logfile = xprocess.ensure("setup_server", Starter)

    yield

    xprocess.getinfo("setup_server").terminate()

curl_path = None

@pytest.fixture
def curl_prep():
    global curl_path
    
    if curl_path is None:
        import shutil
        curl_path = shutil.which("curl")

    if curl_path is None:
        raise #can't find curl

_port = 5000
_url = f"http://localhost:{_port}/"
_endpoint = "log"
_host_string = _url + _endpoint

def run_curl(args):
    base_args = [curl_path, _host_string]
    
    #split up the curl command so the shell won't throw a fit
    #see: https://docs.python.org/3/library/shlex.html#shlex.split
    import shlex
    base_args.extend( shlex.split(args) )
    
    import subprocess
    res = subprocess.run(base_args, capture_output=True)

    import json
    return json.loads( res.stdout.decode() )

def make_sample_row():
    import src.Validation_and_Standardization_Handler as vns1
    vns2 = vns1.Validation_and_Standardization()

    return {str(k):"some value" for k in vns2._required_keys}

def make_curl_string(row):
    res = " "
    for k in row.keys():
        res += f"-d '{k}={row[k]}'"
        res += " "
    return res

class Test_integration:
    def test_bad_end_point(self, curl_prep, setup_server):
        base_args = [curl_path, _url + "some_bad_end_point"]
        base_args.append("-X GET")
        
        import subprocess
        res = subprocess.run(base_args, capture_output=True)

        assert "404" in res.stdout.decode()

    def test_no_username_and_password1(self, curl_prep, setup_server):
        res = run_curl("-X GET")

        message = list(res.values())[0]

        assert 'Username and password required' in message

    def test_no_username_and_password2(self, curl_prep, setup_server):
        res = run_curl("-X POST")

        message = list(res.values())[0]

        assert 'Username and password required' in message

    def test_username_and_empty_password1(self, curl_prep, setup_server):
        res = run_curl("--user test:'' -X GET")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_username_and_empty_password2(self, curl_prep, setup_server):
        res = run_curl("--user test:'' -X POST")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_username_and_bad_password1(self, curl_prep, setup_server):
        res = run_curl("--user test:bad -X GET")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_username_and_bad_password2(self, curl_prep, setup_server):
        res = run_curl("--user test:bad -X POST")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_bad_username_and_password1(self, curl_prep, setup_server):
        res = run_curl("--user bad:test -X GET")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_bad_username_and_password2(self, curl_prep, setup_server):
        res = run_curl("--user bad:test -X POST")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_bad_username_and_bad_password1(self, curl_prep, setup_server):
        res = run_curl("--user bad:bad -X GET")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_bad_username_and_bad_password2(self, curl_prep, setup_server):
        res = run_curl("--user bad:bad -X POST")

        message = list(res.values())[0]

        assert 'Incorrect username or password' in message

    def test_empty_get(self, curl_prep, setup_server):
        res = run_curl("--user test:test -X GET")

        assert isinstance(res, list)
        assert len(res) == 0

    def test_empty_post(self, curl_prep, setup_server):
        res = run_curl("--user test:test -X POST")

        assert isinstance(res, list)
        assert len(res) == 0

    def test_search_on_empty_database(self, curl_prep, setup_server):
        row = make_sample_row()
        row["data"] = "bad_search"
        curl_string = make_curl_string(row)
        
        res = run_curl(f"--user test:test {curl_string} -X GET")

        assert isinstance(res, list)
        assert len(res) == 0

    def test_simple_write(self, curl_prep, setup_server):
        #example: [{'data': 'new_data', '_user': 'test', '_timestamp': '2022-04-05T01:50:57.528273'}]

        row = make_sample_row()
        row["data"] = "new_data"
        curl_string = make_curl_string(row)
        
        res = run_curl(f"--user test:test {curl_string} -X POST")

        assert isinstance(res, list)
        assert len(res) == 1

        keys = list(res[0].keys())

        assert "_timestamp" in keys
        assert "_user" in keys
        assert "data" in keys

        assert "new_data" in res[0]["data"]
        assert "test" in res[0]["_user"]

    def test_write_and_read(self, curl_prep, setup_server):
        row = make_sample_row()
        row["data"] = "new_data"
        curl_string = make_curl_string(row)
        
        res1 = run_curl(f"--user test:test {curl_string} -X POST")

        res2 = run_curl("--user test:test -X GET")

        assert isinstance(res2, list)
        assert len(res2) == 1

        keys = list(res2[0].keys())

        assert "data" in keys
        assert "new_data" in res2[0]["data"]

    def test_write_and_search(self, curl_prep, setup_server):
        row = make_sample_row()
        row["data"] = "new_data"
        curl_string = make_curl_string(row)
        
        res1 = run_curl(f"--user test:test {curl_string} -X POST")

        res2 = run_curl("--user test:test -d 'data=new_data' -X GET")

        assert isinstance(res2, list)
        assert len(res2) == 1

        keys = list(res2[0].keys())

        assert "data" in keys
        assert "new_data" in res2[0]["data"]

    def test_write_and_bad_search(self, curl_prep, setup_server):
        row = make_sample_row()
        row["data"] = "new_data"
        curl_string = make_curl_string(row)
        
        res1 = run_curl(f"--user test:test {curl_string} -X POST")

        res2 = run_curl("--user test:test -d 'data=some_fake_data' -X GET")

        assert isinstance(res2, list)
        assert len(res2) == 0

    def test_bad_verb(self, curl_prep, setup_server):
        res1 = run_curl("--user test:test -X DELETE")

        assert isinstance(res1, dict)
        assert len(res1) == 1
        assert "method is not allowed" in list( res1.values() )[0]

    def test_duplicate_data(self, curl_prep, setup_server):
        row = make_sample_row()
        row["data"] = "new_data"
        curl_string = make_curl_string(row)
        
        run_curl(f"--user test:test {curl_string} -X POST")
        run_curl(f"--user test:test {curl_string} -X POST")

        res1 = run_curl("--user test:test -X GET")

        assert len(res1) == 2

    #TODO, this should cause an error: 
    #Database.Malformed_Input: Malformed input. Input should be of the form: -d "key=value"
    #but the current setup doesn't allow us to read such an error
    #need better error reporting from the server in future
    def test_binary_data(self, curl_prep, setup_server):
        row = make_sample_row()
        curl_string = make_curl_string(row)

        from pathlib import Path
        pic_path = Path("./data/61bVaOK46tL._AC_SL1000_.jpg")
        cmd = f"--user test:test {curl_string} \
            --data-binary '@{pic_path.resolve()}' -X POST"

        res = run_curl(cmd)

        assert True #TODO