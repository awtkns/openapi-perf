from ..OpenAPIPerf import OpenAPIPerf
import requests

ENDPOINT_URL = 'http://localhost:5000'
SCHEMA_PATH = '/openapi.json'

def test_schema_endpoint_exists():
    res = requests.get(ENDPOINT_URL + SCHEMA_PATH)

    assert res.status_code == 200
    assert res.json()

    print(res.json())
    assert res.json()['paths']


def test_generation():
    op = OpenAPIPerf(
        endpoint_url = ENDPOINT_URL,
        schema_path = SCHEMA_PATH
    )
    results = op.run()
    print(results)
    assert 1 == 2

    # op.tests = [t1, t2, t3]

    # op.add_test(
    #     endpoint='http://localhost'
    #     method=''
    #     data=,
    #     expected_result,
    #     expected_status_code
    # ),

    # op.run()
    
