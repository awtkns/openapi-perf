<p align="center">
  <img src="assets/logo-light.png" alt="CRUD Router Logo" />
</p>
<h1 align="center" style="margin-bottom: 0; color: black"><strong>OpenAPI Perf</strong></h1>
<p align="center">
  🤖<em> Automatic OpenAPI Performance Testing </em>🤖</br>
</p>
<p align="center">
<img alt="Tests" src="https://github.com/awtkns/openapi-perf/workflows/Python%20application/badge.svg" />
<img alt="Docs" src="https://github.com/awtkns/openapi-perf/workflows/docs/badge.svg" />
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/openapi-perf" />
</p>

---

**Documentation**: <a href="https://openapi-perf.awtkns.com" target="_blank">https://openapi-perf.awtkns.com</a>

**GitHub Action**: <a href="https://github.com/awtkns/openapi-perf-action" target="_blank">https://github.com/awtkns/openapi-perf-action</a>

**Source Code**: <a href="https://github.com/awtkns/openapi-perf" target="_blank">https://github.com/awtkns/openapi-perf</a>

**PyPi Page**: <a href="https://pypi.org/project/openapi-perf/" target="_blank">https://pypi.org/project/openapi-perf/</a>

---

## Installation

<div class="termy">

```console
$ pip install openapi-perf

---> 100%
```

</div>

## Basic Usage
```python
from openapi_perf import OpenAPIPerf

ENDPOINT_URL = "http://localhost:5000"

if __name__ == "__main__":
    # Generating Test Schema
    op = OpenAPIPerf(ENDPOINT_URL)
    
    # Perfomance Testing
    results = op.run()
    
    # Analysing Results
    results.plot()
    results.to_csv("results.csv")
```
