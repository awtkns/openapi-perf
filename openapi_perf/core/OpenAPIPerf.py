from urllib.parse import urljoin
from os import path, mkdir
import json
import requests
import time
from hypothesis import given, settings, strategies as st

REQ_TYPE_MAPPING = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete
}
PARAM_TYPE_MAPPING = {
    "integer": st.integers(),
    "number": st.floats(),
    "string": st.text()
}

class OpenAPIPerf:
    endpoint_url: str
    schema = {}

    resolved_tests = []

    def __init__(self, endpoint_url: str, schema_path: str, results_dir: str = None):
        if not endpoint_url.startswith('http'):
            endpoint_url = "http://" + endpoint_url
        self.endpoint_url = endpoint_url

        schema_url = urljoin(self.endpoint_url, schema_path)

        try:
            self.schema = self.get_api_schema(schema_url)
        except AssertionError:
            if schema_url.endswith('.json'):
                schema_url.removesuffix('.json')
            else:
                schema_url = schema_url + '.json'

            self.schema = self.get_api_schema(schema_url)

        self.generate_tests()

        if results_dir != None:
            if not path.exists(results_dir):
                mkdir(results_dir)
                
            with open(results_dir + '/extended_schema.json', 'w') as out:
                json.dump(self.schema, out)

    @staticmethod
    def get_api_schema(url: str) -> dict:
        res = requests.get(url)
        schema = res.json()

        assert res.status_code == 200, f"Could not reach schema endpoint {url}"
        assert schema, "No Schema was Found"

        return schema

    # Generate the list of property-based tests
    def generate_tests(self):
        for path_name, path_data in self.schema['paths'].items():
            for req_type, req_data in path_data.items():
                if 'x-tests' in req_data:
                    print("tests already found, skipping") # TODO: put this in a logfile
                    continue
                self.schema['paths'][path_name][req_type]['x-tests'] = []
                
                path_tokens = []
                self.resolved_tests = []
                if 'parameters' in req_data:
                    for parameter in req_data['parameters']:
                        if parameter['in'] == 'path': # TODO: when is this false?
                            path_tokens.append((parameter['name'], parameter['schema']['type']))

                component_schema = {}
                if 'requestBody' in req_data:
                    component_schema_name = req_data['requestBody']['content']['application/json']['schema']['$ref'].split('/')[-1]
                    component_schema = self.schema['components']['schemas'][component_schema_name]['properties']

                resolve_test_with_strategies = given(st.data())(self.resolve_test)
                resolve_test_with_strategies(self, path_name, path_tokens, component_schema)

                # Save test to schema
                self.schema['paths'][path_name][req_type]['x-tests'] = self.resolved_tests

    # Replace tokens in path with generated values
    @staticmethod # needed for hypothesis @given to function properly
    @settings(max_examples=100)
    def resolve_test(self, path_name: str, tokens: [(str, str)], component_schema: {}, data):
        for token_name, token_type in tokens:
            replacement = data.draw(PARAM_TYPE_MAPPING[token_type], label = token_name)
            path_name = path_name.replace("{" + token_name + "}", str(replacement))

        test_data = {}
        for component_name, component_data in component_schema.items():
            test_data[component_name] = data.draw(PARAM_TYPE_MAPPING[component_data['type']], label = component_name)

        self.resolved_tests.append({'path': path_name, 'data': test_data})

    # Run tests and return results
    def run(self):
        response_data = []

        # TODO: multi-thread this
        for path_name, path_data in self.schema['paths'].items():
            for req_type, req_data in path_data.items():
                assert 'x-tests' in req_data, f'Test data for {path_name} {req_type} not generated'
                
                execute = REQ_TYPE_MAPPING[req_type]
                for test in req_data['x-tests']:
                    tic = time.perf_counter()
                    response = execute(urljoin(self.endpoint_url, test['path']))
                    toc = time.perf_counter()

                    response_data.append({
                        'path':     test['path'],
                        'data':     test['data'],
                        'response': response,
                        'validity': str(response.status_code) in req_data['responses'],
                        'time':     toc - tic
                    })

        return response_data
