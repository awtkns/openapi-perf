from os import path, mkdir
import pathlib
from urllib.parse import urljoin
import json
import requests
import time
from hypothesis import given, settings, strategies as st

REQ_TYPE_MAPPING = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete,
}
PARAM_TYPE_MAPPING = {
    "integer": st.integers(),
    "number": st.floats(),
    "string": st.text(),
}


class OpenAPIPerf:
    api_schema = {}
    test_schema = {"endpoint_url": "", "tests": []}

    resolved_tests = []

    def __init__(
        self,
        endpoint_url: str = None,
        api_schema_path: str = None,
        test_schema_path: str = None,
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

            self.generate_tests()

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

    # Generate the list of property-based tests
    def generate_tests(self):
        for path_name, path_data in self.api_schema["paths"].items():
            for req_type, req_data in path_data.items():
                if "x-tests" in req_data:
                    print(
                        "tests already found, skipping"
                    )  # TODO: put this in a logfile
                    continue
                self.api_schema["paths"][path_name][req_type]["x-tests"] = []

                path_tokens = []
                query_tokens = []
                self.resolved_tests = []
                if "parameters" in req_data:
                    for parameter in req_data["parameters"]:
                        token = (parameter["name"], parameter["schema"]["type"])
                        if parameter["in"] == "path":
                            path_tokens.append(token)
                        elif parameter["in"] == "query":
                            query_tokens.append(token)
                        # TODO: any more of these?

                component_schema = {}
                if "requestBody" in req_data:
                    component_schema_name = req_data["requestBody"]["content"][
                        "application/json"
                    ]["schema"]["$ref"].split("/")[-1]
                    component_schema = self.api_schema["components"]["schemas"][
                        component_schema_name
                    ]["properties"]

                resolve_test_with_strategies = given(st.data())(self.resolve_test)
                resolve_test_with_strategies(
                    self, path_name, path_tokens, query_tokens, component_schema
                )

                # Save test to schema
                self.api_schema["paths"][path_name][req_type][
                    "x-tests"
                ] = self.resolved_tests

    # Replace tokens with generated values
    @staticmethod  # needed for hypothesis @given to function properly
    @settings(max_examples=100)
    def resolve_test(
        self,
        path_name: str,
        path_tokens: [(str, str)],
        query_tokens: [(str, str)],
        component_schema: {},
        data,
    ):

        # Path tokens
        for token_name, token_type in path_tokens:
            replacement = data.draw(PARAM_TYPE_MAPPING[token_type], label=token_name)
            path_name = path_name.replace("{" + token_name + "}", str(replacement))

        # Query tokens
        separator = "?"
        for token_name, token_type in query_tokens:
            token_value = data.draw(PARAM_TYPE_MAPPING[token_type], label=token_name)
            path_name = path_name + separator + token_name + "=" + str(token_value)
            separator = "&"

        # Component data
        test_data = {}
        for component_name, component_data in component_schema.items():
            test_data[component_name] = data.draw(
                PARAM_TYPE_MAPPING[component_data["type"]], label=component_name
            )

        self.resolved_tests.append({"path": path_name, "data": test_data})

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
