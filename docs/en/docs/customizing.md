OpenAPI-Perf includes default test generation for APIs based on a OpenAPI spec provided in initialization. That is, when you run
```Python
op = OpenAPIPerf(
    endpoint_url=ENDPOINT_URL,
    results_dir=RESULTS_DIR,
)
```
OP will read the OpenAPI schema found at ```ENDPOINT_URL/openapi.json```, generate a test schema for the endpoint, and save the test schema in ```RESULTS_DIR/test_schema.json```. This schema can be changed to enable custom API tests to be run.

## Test Schema json format
Below is a sample test_schema.json file which is used to execute tests against the ```localhost:5000``` endpoint. It tests 2 paths: ```/potato``` and ```/potato{item_id}```. 

The ```/potato``` route has 2 test plans, the first consisting of a GET followed by a POST, and the second consisting of only a GET. 

We can see that the GET request is configured to have 2 query parameters, skip and limit which are ```skip=0``` & ```limit=0``` in the first test plan, and ```skip=1``` & ```limit=5``` in the second test plan. Both GET requests are expected to return 200 or 422 status codes.

The first test plan for ```/potato``` also has a POST request, which sends some JSON data, in this case the thickness, mass, colour, and type of the potato being posted. 

Finally, we can see that the ```/potato/{item_id}``` has only one test plan, consisting of one GET request. This request includes a path parameter, so ```{item_id}``` was replaced with ```0```.

```json
{
    "endpoint_url": "http://localhost:5000",
    "paths": {
        "/potato": [
            [
                {
                    "type": "get",
                    "path": "/potato?skip=0&limit=0",
                    "data": {},
                    "expected": [
                        "200",
                        "422"
                    ]
                },
                {
                    "type": "post",
                    "path": "/potato",
                    "data": {
                        "thickness": 3.4,
                        "mass": 5.0,
                        "color": "Yellow",
                        "type": "Round"
                    },
                    "expected": [
                        "200",
                        "422"
                    ]
                }
            ],
            [
                {
                    "type": "get",
                    "path": "/potato?skip=1&limit=5",
                    "data": {},
                    "expected": [
                        "200",
                        "422"
                    ]
                }
            ]
        ],
        "/potato/{item_id}": [
            [
                {
                    "type": "get",
                    "path": "/potato/5",
                    "data": {},
                    "expected": [
                        "200",
                        "422"
                    ]
                }
            ]
        ]
    }
}
```

All this data was parameterized based on the OpenAPI schema, but it can be modified to enable custom tests, and run like this:

```Python
op = OpenAPIPerf(
    test_schema_path=RESULTS_DIR + "/test_schema.json",
)
results = op.run()
```