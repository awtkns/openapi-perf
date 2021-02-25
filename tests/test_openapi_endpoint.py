import requests


def test_schema_endpoint_exists():
    res = requests.get('http://localhost:5000/openapi.json')

    assert res.status_code == 200
    assert res.json()
    assert res.json()['paths']
