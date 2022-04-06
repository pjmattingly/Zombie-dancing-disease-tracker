import pytest

#TODO
#We should spin up the server in another script that times out waiting for
#input, rather than here in the testing script
#As it is we risk leaving a running server orphaned if the testing dies

#TODO
#replace these `raise`s with proper exceptions

test_server = None

@pytest.fixture
def setup_server(tmp_path):
    from pathlib import Path
    app_path = Path.cwd() / "main.py"

    if not app_path.exists():
        raise #can't find main entry point for testing

    import shutil
    python_path = shutil.which("python")

    if python_path is None:
        raise #can't find Python

    #start the server and save the database to a temporary path for easy cleanup
    global test_server
    import subprocess
    cmd = [ python_path, str(app_path), str(tmp_path.resolve()) ]
    test_server = subprocess.Popen(cmd)

    #wait for server to start
    while True:
        if not test_server is None:
            first_check = (test_server.returncode is None)
            second_check = (not test_server.pid is None) and \
                (test_server.pid >= 0)
            if first_check and second_check:
                break
        import time
        time.sleep(.1)
    
    yield

    test_server.terminate()
    test_server = None

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

class Test_integration:
    #example: curl http://localhost:5000/log -d "key=test" -X GET

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

    def test_empty_get(self, curl_prep, setup_server):
        res = run_curl("--user test:test -X GET")

        assert isinstance(res, list)
        assert len(res) == 0

    def test_empty_post(self, curl_prep, setup_server):
        res = run_curl("--user test:test -X POST")

        assert isinstance(res, list)
        assert len(res) == 0

    def test_search_on_empty_database(self, curl_prep, setup_server):
        res = run_curl("--user test:test -d 'data=bad_search' -X GET")

        assert isinstance(res, list)
        assert len(res) == 0

    def test_simple_write(self, curl_prep, setup_server):
        #example: [{'data': 'new_data', '_user': 'test', '_timestamp': '2022-04-05T01:50:57.528273'}]
        res = run_curl("--user test:test -d 'data=new_data' -X POST")

        assert isinstance(res, list)
        assert len(res) == 1

        print(res)
        raise