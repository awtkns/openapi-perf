from hypothesis import given, settings, strategies as st
from typing import Dict, List, Any

NUM_TESTS = 100

PARAM_TYPE_MAPPING = {
    "integer": st.integers(min_value=-2**63, max_value=2**63-1),
    "number": st.floats(),
    "string": st.text(),
}


class Generator:

    def __init__(self) -> None:
        self.resolve_data_with_strategy = None
        self.resolved_data_return: List[Dict[str, Any]] = []

    # Generate test schema of property-based tests
    def generate_tests(self, api_schema: {}):
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
                generated_requests = [{"type": req_type, "path": path_name, "data": {}} for _ in range(NUM_TESTS)] 

                # parse request parameters
                if "parameters" in req_data:
                    for parameter in req_data["parameters"]:

                        # resolve parameter to data
                        parameter_id = parameter["in"] + '/' + parameter["name"]
                        if not parameter_id in tokens:
                            tokens[parameter_id] = self.resolve_data_and_return(
                                parameter_id, parameter["schema"]["type"]
                            )

                        # add parameter to paths
                        generated_requests = self.add_tokens(
                            generated_requests, 
                            tokens[parameter_id], 
                            parameter['in'], 
                            parameter["name"],
                        )

                # parse request components
                if "requestBody" in req_data:
                    component_schema_name = req_data["requestBody"]["content"]["application/json"]["schema"]["$ref"].split("/")[-1]
                    component_schema = api_schema["components"]["schemas"][component_schema_name]["properties"]
                    # TODO: can a request have multiple components? Assuming no..

                    # resolve component
                    if not component_schema_name in component_schemas:
                        generated_component = {}
                        for component_param_name, component_param_data in component_schema.items():
                            generated_component[component_param_name] = self.resolve_data_and_return(
                                "component/" + component_schema_name + component_param_name,
                                component_param_data["type"]
                            )

                        component_schemas[component_schema_name] = generated_component

                    generated_requests = self.add_tokens(
                        generated_requests, 
                        component_schemas[component_schema_name], 
                        "component", 
                        "",
                    )

                total_generated_requests[req_type] = generated_requests

            # create default test plan: 
            # get, put, get, post, get, delete, get
            tests = []
            get_exists = 'get' in total_generated_requests
            if get_exists:
                get = total_generated_requests['get']
                if get_exists:
                    tests.append(get) 
            if 'put' in total_generated_requests:
                tests.append(total_generated_requests['put'])
                if get_exists:
                    tests.append(get) 
            if 'post' in total_generated_requests:
                tests.append(total_generated_requests['post']) 
                if get_exists:
                    tests.append(get) 
            if 'delete' in total_generated_requests:
                tests.append(total_generated_requests['delete']) 
                if get_exists:
                    tests.append(get) 

            # reshape test list
            tests = list(zip(*tests))

            test_schema["paths"][path_name] = tests

        return test_schema

    # Wrapper for the static resolve_data function
    # Necessary to enable Hypothesis to return generated values
    def resolve_data_and_return(self, data_name: str, data_type: str):
        self.resolved_data_return = []
        self.resolve_data_with_strategy(self, data_name, data_type)
        assert len(self.resolved_data_return) == NUM_TESTS, f"Hypothesis didn't generate {NUM_TESTS} values"
        return self.resolved_data_return

    # Generate property-based data of a given type
    @staticmethod
    @settings(max_examples=NUM_TESTS)
    def resolve_data(self, data_name: str, data_type: str, data: st.data):
        self.resolved_data_return.append(data.draw(PARAM_TYPE_MAPPING[data_type], label=data_name))

    # Add a parameter token to a request
    @staticmethod
    def add_tokens(requests: [{}], token_values: [], token_type: str, token_name: str):
        for i in range(len(requests)):
            if token_type == "path":
                requests[i]["path"] = requests[i]["path"].replace("{" + token_name + "}", str(token_values[i]))
            elif token_type == "query":
                separator = '&' if '?' in requests[i]["path"] else '?'
                requests[i]["path"] = requests[i]["path"] + separator + token_name + "=" + str(token_values[i])
            elif token_type == "component":
                requests[i]["data"] = {param_name: param_data[i] for param_name, param_data in token_values.items()}
            else:
                raise Exception("Unexpected parameter token type")

        return requests
