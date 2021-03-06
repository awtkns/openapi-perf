from urllib.parse import urljoin
import requests
from hypothesis import given, strategies as st

REQ_TYPE_MAPPING = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete
}
PARAM_TYPE_MAPPING = {
    "integer": st.integers
}

class OpenAPIPerf:
    endpoint_url = ''
    schema = {}

    resolved_path_name = ''

    def __init__(self, endpoint_url='', schema_path='', generate=True):
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

        if generate: self.generate_tests()

    @staticmethod
    def get_api_schema(url) -> dict:
        res = requests.get(url)
        schema = res.json()

        assert res.status_code == 200, f"Could not reach schema endpoint {url}"
        assert schema, "No Schema was Found"

        return schema

    # Generate the list of property-based tests
    def generate_tests(self):
        for path_name, path_data in self.schema['paths'].items():
            for req_type, req_data in path_data.items():
                
                self.resolved_path_name = path_name
                if 'parameters' in req_data:
                    for parameter in req_data['parameters']:
                        if parameter['in'] == 'path':
                            strategy = PARAM_TYPE_MAPPING[parameter['schema']['type']]()
                            resolve_path_with_strategy = given(strategy)(self.resolve_path)
                            resolve_path_with_strategy(self, path_name, parameter['name'])
                        
                        # TODO: support parameters which are not part of path

                # Save test to schema
                self.schema['paths'][path_name][req_type]['x-tests'] = [{"path": self.resolved_path_name, "data": 0}]

    # Replace token in path with a value
    @staticmethod # needed for hypothesis @given to function properly
    def resolve_path(self, path_name, parameter_name, parameter_value):
        self.resolved_path_name = path_name.replace("{" + parameter_name + "}", str(parameter_value))

    # Run tests and return results
    def run(self):

        response_data = []

        # TODO: multi-thread this
        for path_name, path_data in self.schema['paths'].items():
            for req_type, req_data in path_data.items():

                assert 'x-tests' in req_data, f'Test data not generated'
                for test in req_data['x-tests']:
                    print(test['path'])
                    execute = REQ_TYPE_MAPPING[req_type]
                    response = execute(urljoin(self.endpoint_url, test['path']))
                    response_data.append(response)

        return response_data
