from typing import Dict, Any, Callable, List

from urllib.parse import urljoin
import requests
import time

REQ_TYPE_MAPPING: Dict[str, Callable[[Any], Any]] = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete,
}

DICT = Dict[str, Any]


def execute(test_schema: DICT, api_schema: DICT) -> List[DICT]:
    endpoint_url = test_schema["endpoint_url"]
    response_data = []

    # TODO: multi-thread this
    for path_name, path_data in api_schema["paths"].items():
        for req_type, req_data in path_data.items():
            assert (
                "x-tests" in req_data
            ), f"Test data for {path_name} {req_type} not generated"

            request = REQ_TYPE_MAPPING[req_type]
            for test in req_data["x-tests"]:
                response: requests.Response = request(urljoin(endpoint_url, test["path"]))

                response_data.append(
                    {
                        "method": response.request.method,
                        "path": test["path"],
                        "data": test["data"],
                        "response": response,
                        "response_data": response.json(),
                        "status_code": response.status_code,
                        "validity": str(response.status_code) in req_data["responses"],
                        "time": response.elapsed.total_seconds()
                    }
                )
    
    return response_data
