from pytest import mark

from openapi_perf.core import _utils


def test_sanitize_url(url: str = "localhost:5000"):
    url = _utils.sanitize_endpoint_url(url)

    assert url.startswith("http://")
    return url


@mark.parametrize("api_schema_path", ["/openapi", "openapi", "openapi.json"])
@mark.parametrize(
    "endpoint",
    ["localhost:5000", "127.0.0.1:5000", "localhost:5000/", "http://localhost:5000/"],
)
def test_retrieve_api_schema(endpoint: str, api_schema_path: str):
    endpoint = test_sanitize_url(endpoint)

    schema = _utils.get_api_schema(endpoint, api_schema_path)
    assert type(schema) is dict

    return schema
