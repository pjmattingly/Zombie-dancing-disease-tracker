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
    curl_prep()

    base_args = [curl_path, _host_string]
    
    #split up the curl command so the shell won't throw a fit
    #see: https://docs.python.org/3/library/shlex.html#shlex.split
    import shlex
    base_args.extend( shlex.split(args) )
    
    import subprocess
    res = subprocess.run(base_args, capture_output=True)

    import json
    return json.loads( res.stdout.decode() )

class Test_integration_rate_limit:
    '''
    TODO
    Here we attempt to test the rate limit on the server
    but my computer seems to have a hard limit of the number of processes
    it can spawn
    and so the rate of requests is capped at ~16 requests per second
    far too slow to really test the rate limiting
    thus, in future, we'd want to run this test on some sort of cluster
    '''
    def test_get_rate_limit(self, setup_server):
        #seed the database
        run_curl("--user test:test -d 'data=new_data' -X POST")

        num_workers = 60

        args = ["--user test:test -X GET"] * num_workers

        from multiprocessing import Pool
        with Pool(processes=num_workers) as pool:
            res2 = pool.map_async(run_curl, args)
            res2.wait() #wait for the results

        assert len(res2.get()) == num_workers