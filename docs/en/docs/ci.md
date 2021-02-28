A github action for openapi-pref has been created to allow you to use openapi-perf in github workflows. Additionally, 
you can install the openapi-perf github app which will automatically comment and upload the generated report. Without the
app installed, the report will be uploaded as a workflow artifact.


---

**Source Code**: <a href="https://github.com/awtkns/openapi-perf-action" target="_blank">https://github.com/awtkns/openapi-perf-action</a>

---

[Add Github Action](https://github.com/apps/openapi-performance-testing){:target="_blank" .md-button .md-button--primary }
[Add Github App](https://github.com/apps/openapi-performance-testing){:target="_blank" .md-button .md-button--primary }


### Example Github Action
```yaml
on: pull_request

jobs:
  openapi-perf:
    name: Builds and Runs the OpenAPI Performance Test Action
    if: ${{ github.event.issue.pull_request }}
    runs-on: ubuntu-latest
    steps:
    - name: OpenAPI Performance Test
      uses: awtkns/openapi-perf-action@main
      with:
        openapi-endpoint: 'http://localhost:5000/openapi.json'
```