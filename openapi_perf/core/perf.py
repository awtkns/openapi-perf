from os import path, mkdir

import json

from typing import Optional

from . import _utils
from ._gen import Generator
from ._exec import execute
from ._types import API_SCHEMA, TEST_SCHEMA, TEST_RESULTS


class OpenAPIPerf:
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
                _utils.validate_test_schema(self.test_schema)

        elif endpoint_url:
            self.endpoint_url = _utils.sanitize_endpoint_url(endpoint_url)
            api_schema = _utils.get_api_schema(self.endpoint_url, api_schema_path)

            if auto_generate:
                self.test_schema = self._generate_test_schema(api_schema)

        else:
            raise ValueError("No test schema or endpoint provided")

        if results_dir:
            self.write_results(results_dir)

    def _generate_test_schema(self, api_schema: API_SCHEMA) -> TEST_SCHEMA:
        """ Generates the tests to be run """
        test_schema = Generator().generate_tests(api_schema)
        test_schema["endpoint_url"] = self.endpoint_url

        return test_schema

    # Run tests and return results
    def run(self) -> TEST_RESULTS:
        return execute(self.test_schema)

    def write_results(self, results_dir: str) -> None:
        if not path.exists(results_dir):
            mkdir(results_dir)

        with open(results_dir + "/test_schema.json", "w") as out:
            json.dump(self.test_schema, out)
