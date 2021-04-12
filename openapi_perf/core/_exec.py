from typing import Dict, Any, Callable
from urllib.parse import urljoin

import requests

from ._types import TEST_RESULTS

REQ_TYPE_MAPPING: Dict[str, Callable[[Any], Any]] = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete,
}


def execute(test_schema: Dict[str, Any]) -> TEST_RESULTS:
    endpoint_url = test_schema["endpoint_url"]
    response_data = []

    # TODO: multi-thread this
    for path_name, path_tests in test_schema["paths"].items():
        for test in path_tests:
            for request in test:
                make_request = REQ_TYPE_MAPPING[request["type"]]
                url = urljoin(endpoint_url, request["path"])



                # noinspection PyArgumentList
                print(request["data"])
                for key in request["data"]:
                    print(type(request["data"][key]))

                data = request["data"]

                response: requests.Response = make_request(
                    url, json=data,  headers={'Content-Type': 'application/json; charset=UTF-8'},
                )  # type: ignore


                info = {
                        "type": request["type"],
                        "path_name": path_name,
                        "path": request["path"],
                        "data": request["data"],
                        "response": response,
                        "status_code": response.status_code,
                        "validity": str(response.status_code) in request["expected"],
                        "time": response.elapsed.total_seconds(),
                    }

                try:
                    info["response_data"] = response.json()
                except Exception:
                    pass

                response_data.append(info)

    return response_data
