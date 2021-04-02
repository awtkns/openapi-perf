from openapi_perf import OpenAPIPerf
import pathlib
import requests
import pandas as pd

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
        api_schema_path=API_SCHEMA_PATH,
        results_dir=str(pathlib.Path(__file__).parent.absolute()) + "/sample_results",
    )
    results = op.run()

    pd.set_option("display.max_columns", None)
    print(pd.DataFrame(results))


# def test_importing():
#     op = OpenAPIPerf(
#         test_schema_path = str(pathlib.Path(__file__).parent.absolute()) + '/sample_results/test_schema.json'
#     )
#     results = op.run()

#     pd.set_option('display.max_columns', None)
#     print(pd.DataFrame(results))
