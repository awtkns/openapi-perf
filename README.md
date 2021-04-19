<p align="center">
  <img src="./docs/en/docs/assets/logo-light.png" alt="OpenAPI Perf Logo" />
</p>
<h3 align="center" style="margin-bottom: 0; color: black"><strong>OpenAPI Perf</strong></h3>
<p align="center">
  🤖<em> Automatic OpenAPI Performance Testing </em>🤖</br>
</p>
<p align="center">
<img alt="Tests" src="https://github.com/awtkns/openapi-perf/workflows/Tests/badge.svg" />
<img alt="Docs" src="https://github.com/awtkns/fastapi-crudrouter/workflows/docs/badge.svg" />
<a href="https://pypi.org/project/openapi-perf" target="_blank">
  <img src="https://img.shields.io/pypi/v/openapi-perf?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<img alt=Python Version" src="https://img.shields.io/pypi/pyversions/openapi-perf?color=%2334D058" />
</p>

---

**Documentation**: <a href="https://openapi-perf.awtkns.com" target="_blank">https://openapi-perf.awtkns.com</a>

**Source Code**: <a href="https://github.com/awtkns/openapi-perf" target="_blank">https://github.com/awtkns/openapi-perf</a>

**Continous Integration**: <a href="https://github.com/awtkns/openapi-perf-action" target="_blank">https://github.com/awtkns/openapi-perf-action</a>

---


This project will make use of the OpenAPI schema to build an automated REST API performance testing and benchmarking tool. OpenAPI defines an interface for REST APIs allowing automated generation of an API schema which provides insights on the API's usage and expected input and response values. Using the OpenAPI schema we hope automatically generate tests covering all endpoints. We will use these generated tests to both test for endpoint correctness and to gather relevant performance metrics such as response time. We will finally generate an informative report on endpoint performance and correctness, allowing developers to quickly determine potentially problematic endpoints and endpoints that would benefit most from optimization.

## Installation
```python
pip install openapi-perf
```

## Usage
### Test Generation
This will create generate property-based performance tests for an endpoint and save the test schema to your results directory.
```python
from openapi_perf import OpenAPIPerf

op = OpenAPIPerf(
  endpoint_url = "http://localhost:5000",
  results_dir = "/path/to/results/directory"
)
```

You can also load existing tests from a test schema file like this:
```python
op = OpenAPIPerf(
  test_schema_path = "path/to/test_schema.json"
)
```
Schema files can be modified to configure test execution.

### Test Execution

To run these tests, use
```python
op.run()
```

This will generate a report pdf file in your results directory

For detailed usage, refer to our [docs](https://openapi-perf.awtkns.com)
