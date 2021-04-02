from pytest import mark

from openapi_perf import OpenAPIPerf


@mark.parametrize("api_schema_path", ["/openapi", "openapi", "openapi.json"])
@mark.parametrize(
    "endpoint",
    ["localhost:5000", "127.0.0.1:5000", "localhost:5000/", "http://localhost:5000/"],
)
def test_endpoint_path_valid(endpoint, api_schema_path):
    OpenAPIPerf(endpoint_url=endpoint, api_schema_path=api_schema_path)
