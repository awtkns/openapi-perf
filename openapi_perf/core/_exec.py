from typing import Dict, Any, Callable, List
from urllib.parse import urljoin

import concurrent.futures
import threading
import requests

from .results import PerfResults
from .schemas import TestSchema

REQ_TYPE_MAPPING: Dict[str, Callable[[Any], Any]] = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete,
}


class Executor:
    _lock: threading.Lock
    endpoint_url: str
    response_data: List[Any]

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def execute(self, test_schema: TestSchema) -> PerfResults:
        self.endpoint_url = test_schema.endpoint_url
        self.response_data = []

        with concurrent.futures.ThreadPoolExecutor() as tp_executor:
            for path_name, path_tests in test_schema.paths.items():
                for test in path_tests:
                    for request in test:
                        request["base_path_name"] = path_name
                tp_executor.map(self.execute_test, path_tests)

        return PerfResults(self.response_data)

    def execute_test(self, test: List[Dict[str, Any]]) -> None:
        for request in test:
            make_request = REQ_TYPE_MAPPING[request["type"]]
            url = urljoin(self.endpoint_url, request["path"])

            data = request["data"]

            response: requests.Response = make_request(
                url,
                json=data,
                headers={"Content-Type": "application/json; charset=UTF-8"},
            )  # type: ignore

            info = {
                "type": request["type"],
                "path_name": request["base_path_name"],
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
                info["response_data"] = None
                pass

            with self._lock:
                self.response_data.append(info)
