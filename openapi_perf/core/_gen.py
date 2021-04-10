from hypothesis import given, settings, strategies as st
from typing import Dict, List, Any, Callable, Optional, Union

from ._types import TEST_SCHEMA, API_SCHEMA

NUM_TESTS = 100
PARAM_TYPE_MAPPING = {
    "integer": st.integers(min_value=-(2 ** 63), max_value=2 ** 63 - 1),
    "number": st.floats(),
    "string": st.text(),
}


class Generator:
    TOKEN_TYPES = {"path", "query", "component"}
    DEFAULT_TEST_ORDER = ["get", "put", "get", "post", "get", "delete", "get"]

    def __init__(self) -> None:
        self.resolve_data_with_strategy: Callable = None
        self.resolved_data_return: List[Dict[str, Any]] = []

    def generate_tests(self, api_schema: API_SCHEMA) -> TEST_SCHEMA:
        """ Generate test schema of property-based tests """

        test_schema = {
            "endpoint_url": "",
            "paths": {},
        }

        # parse paths
        for path_name, path_data in api_schema["paths"].items():
            tokens = {}
            component_schemas = {}
            total_generated_requests = {}

            # reset data generation strategy
            self.resolve_data_with_strategy = given(st.data())(self.resolve_data)

            # parse request types
            for req_type, req_data in path_data.items():
                generated_requests = [
                    {
                        "type": req_type,
                        "path": path_name,
                        "data": {},
                        "expected": list(req_data["responses"].keys())
                        if "responses" in req_data
                        else [],
                    }
                    for _ in range(NUM_TESTS)
                ]

                # parse request parameters
                if "parameters" in req_data:
                    for parameter in req_data["parameters"]:

                        # resolve parameter to data
                        parameter_id = parameter["in"] + "/" + parameter["name"]
                        if parameter_id not in tokens:
                            tokens[parameter_id] = self.resolve_data_and_return(
                                parameter_id, parameter["schema"]["type"]
                            )

                        # add parameter to paths
                        generated_requests = self.add_tokens(
                            generated_requests,
                            tokens[parameter_id],
                            parameter["in"],
                            parameter["name"],
                        )

                # parse request components
                if "requestBody" in req_data:
                    component_schema_name = req_data["requestBody"]["content"][
                        "application/json"
                    ]["schema"]["$ref"].split("/")[-1]
                    component_schema = api_schema["components"]["schemas"][
                        component_schema_name
                    ]["properties"]
                    # TODO: can a request have multiple components? Assuming no..

                    # resolve component
                    if component_schema_name not in component_schemas:
                        generated_component = {}
                        for (
                            component_param_name,
                            component_param_data,
                        ) in component_schema.items():
                            generated_component[
                                component_param_name
                            ] = self.resolve_data_and_return(
                                "component/"
                                + component_schema_name
                                + component_param_name,
                                component_param_data["type"],
                            )

                        component_schemas[component_schema_name] = generated_component

                    generated_requests = self.add_tokens(
                        generated_requests,
                        component_schemas[component_schema_name],
                        "component",
                        "",
                    )

                total_generated_requests[req_type] = generated_requests

            tests = self.build_test_plan(total_generated_requests)

            # reshape test list
            tests = list(zip(*tests))

            test_schema["paths"][path_name] = tests

        return test_schema

    @staticmethod
    def build_test_plan(generated_requests, test_order: List[str] = None) -> List[Any]:
        """ Creates a test plan following a pre-defined test order """

        test_order = test_order or Generator.DEFAULT_TEST_ORDER
        methods_under_test = {
            method: generated_requests.get(method, None) for method in set(test_order)
        }

        tests = [
            methods_under_test[method]
            for method in test_order
            if methods_under_test[method]
        ]

        return tests

    def resolve_data_and_return(self, data_name: str, data_type: str):
        """
        Wrapper for the static resolve_data function
        Necessary to enable Hypothesis to return generated values
        """

        self.resolved_data_return = []
        self.resolve_data_with_strategy(self, data_name, data_type)
        assert (
            len(self.resolved_data_return) == NUM_TESTS
        ), f"Hypothesis didn't generate {NUM_TESTS} values"
        return self.resolved_data_return

    @staticmethod
    @settings(max_examples=NUM_TESTS)
    def resolve_data(self, data_name: str, data_type: str, data: st.data):
        """ Generate property-based data of a given type """

        self.resolved_data_return.append(
            data.draw(PARAM_TYPE_MAPPING[data_type], label=data_name)
        )

    @staticmethod
    def _build_query_params(
        path: str, token_type: str, token_name: str, token_value: Any
    ) -> str:
        if token_type == "path":
            return path.replace(f"{{{token_name}}}", str(token_value))

        elif token_type == "query":
            separator = "&" if "?" in path else "?"
            return f"{path}{separator}{token_name}={token_value}"

        else:
            return path

    @staticmethod
    def add_tokens(
        requests: List[Dict[str, Any]],
        token_values: Union[List[Any], Dict[str, Any]],
        token_type: str,
        token_name: str,
    ) -> List[Dict[str, Any]]:
        """ Add a parameter token to a request """
        assert token_type in Generator.TOKEN_TYPES

        for i, request in enumerate(requests):
            if token_type == "component":
                requests[i]["data"] = {
                    param_name: param_data[i]
                    for param_name, param_data in token_values.items()
                }
            else:
                requests[i]["path"] = Generator._build_query_params(
                    request["path"], token_type, token_name, token_values[i]
                )

        return requests
