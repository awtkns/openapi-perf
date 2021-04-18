from os import path, mkdir
from typing import Optional

from . import _utils
from .results import PerfResults
from ._exec import Executor
from ._gen import Generator
from ._types import API_SCHEMA
from .schemas import TestSchema


class OpenAPIPerf:
    test_schema: TestSchema
    endpoint_url: str

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        api_schema_path: str = "/openapi.json",
        test_schema_path: Optional[str] = None,
        results_dir: Optional[str] = None,
    ):
        if test_schema_path:
            self.test_schema = TestSchema.load(test_schema_path)

        elif endpoint_url:
            self.endpoint_url = _utils.sanitize_endpoint_url(endpoint_url)

            api_schema = _utils.get_api_schema(self.endpoint_url, api_schema_path)
            self.test_schema = self._generate_test_schema(api_schema)

        else:
            raise ValueError("No test schema or endpoint provided")

        if results_dir:
            self.write_results(results_dir)

    def _generate_test_schema(self, api_schema: API_SCHEMA) -> TestSchema:
        """ Generates the tests to be run """
        test_schema = Generator().generate_tests(api_schema, self.endpoint_url)

        return test_schema

    # Run tests and return results
    def run(self) -> PerfResults:
        return Executor().execute(self.test_schema)

    def write_results(self, results_dir: str) -> None:
        if not path.exists(results_dir):
            mkdir(results_dir)

        self.test_schema.save(f"{results_dir}/test_schema.json")
