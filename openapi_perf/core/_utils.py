from urllib.parse import urljoin

import requests

from ._types import API_SCHEMA, TEST_SCHEMA


def validate_test_schema(test_schema: TEST_SCHEMA) -> bool:
    try:
        assert type(test_schema) is dict
        assert type(test_schema.get("endpoint_url")) is str
        assert type(test_schema.get("paths")) is dict
    except AssertionError:
        raise ValueError("Invalid Test Schema Provided")

    return True


def sanitize_endpoint_url(endpoint_url: str) -> str:
    if not endpoint_url.startswith("http"):
        endpoint_url = "http://" + endpoint_url

    return endpoint_url


def get_api_schema(endpoint_url: str, api_schema_path: str) -> API_SCHEMA:
    """ Gets an API Schema From an endpoint """

    if not api_schema_path.endswith(".json"):
        api_schema_path = api_schema_path + ".json"

    url = urljoin(endpoint_url, api_schema_path)
    res = requests.get(url)

    if not res.status_code == 200:
        raise Exception(f"Could not reach schema endpoint {url}")

    api_schema: API_SCHEMA = res.json()
    if not api_schema:
        raise Exception("No schema was found")

    return api_schema
