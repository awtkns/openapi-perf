from pytest import raises

from openapi_perf.core.schemas import TestSchema


def test_validate_test_schema():
    schema = {"endpoint_url": "http://localhost:5000/", "paths": {}}

    assert TestSchema.validate_test_schema(schema)


def test_validate_test_schema_fail():
    schema = {}

    with raises(ValueError):
        TestSchema.validate_test_schema(schema)
