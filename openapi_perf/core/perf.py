from os import path, mkdir
from urllib.parse import urljoin
import json
import requests
from typing import Optional

from ._gen import Generator
from ._exec import execute
from ._types import API_SCHEMA, TEST_SCHEMA, TEST_RESULTS


class OpenAPIPerf:
    api_schema: API_SCHEMA = {}
    test_schema: TEST_SCHEMA = {}

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        api_schema_path: str = "/openapi.json",
        test_schema_path: Optional[str] = None,
        results_dir: Optional[str] = None,
        auto_generate: bool = True,  # Added to disable test generation for unit testing
    ):

        if test_schema_path:
            assert path.exists(
                test_schema_path
            ), f"Test schema not found at {test_schema_path}"

            with open(test_schema_path) as f:
                self.test_schema = json.load(f)

        elif endpoint_url:
            self.endpoint_url = self.sanitize_endpoint_url(endpoint_url)
            self.api_schema = self.get_api_schema(self.endpoint_url, api_schema_path)

            if auto_generate:
                self._generate()

        else:
            raise ValueError(f"No test schema or endpoint provided")

        if results_dir:
            self.write_results(results_dir)

    @staticmethod
    def sanitize_endpoint_url(endpoint_url: str) -> str:
        if not endpoint_url.startswith("http"):
            endpoint_url = "http://" + endpoint_url

        return endpoint_url

    @staticmethod
    def get_api_schema(endpoint_url: str, api_schema_path: str) -> API_SCHEMA:
        if not api_schema_path.endswith(".json"):
            api_schema_path = api_schema_path + ".json"

        api_schema_url = urljoin(endpoint_url, api_schema_path)

        res = requests.get(api_schema_url)
        if not res.status_code == 200:
            raise Exception(f"Could not reach schema endpoint {api_schema_url}")

        api_schema: API_SCHEMA = res.json()
        if not api_schema:
            raise Exception("No schema was found")

        return api_schema

    def _generate(self) -> None:
        """ Generates the tests to be run """
        self.test_schema = Generator().generate_tests(self.api_schema)
        self.test_schema["endpoint_url"] = self.endpoint_url

    # Run tests and return results
    def run(self) -> TEST_RESULTS:
        return execute(self.test_schema)

    def write_results(self, results_dir: str) -> None:
        if not path.exists(results_dir):
            mkdir(results_dir)

        with open(results_dir + "/test_schema.json", "w") as out:
            json.dump(self.test_schema, out)
