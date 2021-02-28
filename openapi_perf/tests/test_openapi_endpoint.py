import requests
from .. import OpenAPIPerf

SCHEMA_URL = 'http://localhost:5000/openapi.json'

def test_schema_endpoint_exists():
    res = requests.get(SCHEMA_URL)

    assert res.status_code == 200
    assert res.json()

    print(res.json())
    assert res.json()['paths']


def test_generation():
    # op = OpenAPIPerf(
    #     schema_url=SCHEMA_URL
    # )

    # op.tests = [t1, t2, t3]

    # op.add_test(
    #     endpoint='http://localhost'
    #     method=''
    #     data=,
    #     expected_result,
    #     expected_status_code
    # ),

    # op.run()
    
