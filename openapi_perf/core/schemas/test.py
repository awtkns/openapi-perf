import json
import os

from typing import List, Dict, Any

from .._types import TEST_SCHEMA


class TestSchema:
    _endpoint_url: str
    _paths: Dict[str, List[Any]]

    def __init__(self, endpoint_url: str) -> None:
        self._endpoint_url = endpoint_url
        self._paths = {}

    def add_tests(self, path: str, tests: List[Any]) -> None:
        self._paths[path] = tests

    def to_json(self) -> TEST_SCHEMA:
        return {"endpoint_url": self._endpoint_url, "paths": self._paths}

    def save(self, path: str) -> None:
        with open(path, "w") as fp:
            json.dump(self.to_json(), fp)

    @staticmethod
    def load(path: str) -> "TestSchema":
        assert os.path.exists(path), f"Test schema not found at {path}"

        with open(path) as fp:
            data = json.load(fp)

            TestSchema.validate_test_schema(data)
            schema = TestSchema(data.get("endpoint_url"))
            schema._paths = data.get("paths")
            return schema

    @staticmethod
    def validate_test_schema(test_schema: TEST_SCHEMA) -> bool:
        try:
            assert type(test_schema) is dict
            assert type(test_schema.get("endpoint_url")) is str
            assert type(test_schema.get("paths")) is dict
        except AssertionError:
            raise ValueError("Invalid Test Schema Provided")

        return True

    @property
    def endpoint_url(self) -> str:
        return self._endpoint_url

    @property
    def paths(self) -> Dict[str, List[Any]]:
        return self._paths
