import requests

from openapi_perf import OpenAPIPerf
from tests import RESULTS_DIR

ENDPOINT_URL = "http://localhost:5000"
API_SCHEMA_PATH = "/openapi.json"


def test_schema_endpoint_exists():
    res = requests.get(ENDPOINT_URL + API_SCHEMA_PATH)

    assert res.status_code == 200
    assert res.json()

    print(res.json())
    assert res.json()["paths"]


def test_generation():
    op = OpenAPIPerf(
        endpoint_url=ENDPOINT_URL,
        results_dir=RESULTS_DIR,
    ).run()


def test_restoration():
    op = OpenAPIPerf(
        test_schema_path=RESULTS_DIR + "/test_schema.json",
        results_dir=RESULTS_DIR,
    )
    results = op.run()
    results.to_csv(RESULTS_DIR + "/results.csv")
