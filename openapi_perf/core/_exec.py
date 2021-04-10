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


def execute(test_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    endpoint_url = test_schema["endpoint_url"]
    response_data = []

    # TODO: multi-thread this
    for path_name, path_tests in test_schema["paths"].items():
        for test in path_tests:
            for request in test:
                make_request = REQ_TYPE_MAPPING[request["type"]]
                url = urljoin(endpoint_url, request["path"])

                # noinspection PyArgumentList
                response: requests.Response = make_request(
                    url, data=request["data"]
                )  # typing ignore

                response_data.append(
                    {
                        "type": request["type"],
                        "path_name": path_name,
                        "path": request["path"],
                        "data": request["data"],
                        "response": response,
                        "response_data": response.json(),
                        "status_code": response.status_code,
                        "validity": str(response.status_code) in request["expected"],
                        "time": response.elapsed.total_seconds(),
                    }
                )

    return response_data
