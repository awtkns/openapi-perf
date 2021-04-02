from os import path, mkdir
from urllib.parse import urljoin
import json
import requests
import time

from .Generator import Generator

REQ_TYPE_MAPPING = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete,
}


class OpenAPIPerf:
    api_schema = {}
    test_schema = {"endpoint_url": "", "tests": []}

    def __init__(
        self,
        test_schema_path: str = None,
        endpoint_url: str = None,
        api_schema_path: str = None,
        results_dir: str = None,
    ):

        if test_schema_path:
            if not path.exists(test_schema_path):
                raise ValueError(f"Test schema not found at {test_schema_path}")
            # TODO: read data

        elif endpoint_url and api_schema_path:
            if not endpoint_url.startswith("http"):
                endpoint_url = "http://" + endpoint_url

            self.test_schema["endpoint_url"] = endpoint_url
            self.api_schema = self.get_api_schema(endpoint_url, api_schema_path)

            self.api_schema = Generator().generate_tests(self.api_schema)

        else:
            if api_schema_path:
                raise ValueError(f"No endpoint url provided")
            raise ValueError(f"No schema provided")

        if results_dir:
            self.write_results(results_dir)

    @staticmethod
    def get_api_schema(endpoint_url: str, api_schema_path: str) -> dict:
        if not api_schema_path.endswith(".json"):
            api_schema_path = api_schema_path + ".json"

        api_schema_url = urljoin(endpoint_url, api_schema_path)

        res = requests.get(api_schema_url)
        if not res.status_code == 200:
            raise Exception(f"Could not reach schema endpoint {api_schema_url}")

        api_schema = res.json()
        if not api_schema:
            raise Exception("No schema was found")

        return api_schema

    # Run tests and return results
    def run(self):
        endpoint_url = self.test_schema["endpoint_url"]
        response_data = []

        # TODO: multi-thread this
        for path_name, path_data in self.api_schema["paths"].items():
            for req_type, req_data in path_data.items():
                assert (
                    "x-tests" in req_data
                ), f"Test data for {path_name} {req_type} not generated"

                execute = REQ_TYPE_MAPPING[req_type]
                for test in req_data["x-tests"]:
                    tic = time.perf_counter()
                    response = execute(urljoin(endpoint_url, test["path"]))
                    toc = time.perf_counter()

                    response_data.append(
                        {
                            "path": test["path"],
                            "data": test["data"],
                            "response": response,
                            "validity": str(response.status_code)
                            in req_data["responses"],
                            "time": toc - tic,
                        }
                    )

        return response_data

    def write_results(self, results_dir: str):
        if not path.exists(results_dir):
            mkdir(results_dir)

        with open(results_dir + "/api_schema.json", "w") as out:
            json.dump(self.api_schema, out)

        with open(results_dir + "/test_schema.json", "w") as out:
            json.dump(self.test_schema, out)
