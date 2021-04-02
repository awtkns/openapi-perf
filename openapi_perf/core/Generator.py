from hypothesis import given, settings, strategies as st

PARAM_TYPE_MAPPING = {
    "integer": st.integers(),
    "number": st.floats(),
    "string": st.text()
}

class Generator:

    resolved_tests = []

    # Generate the list of property-based tests
    def generate_tests(self, api_schema: {}):
        for path_name, path_data in api_schema['paths'].items():
            for req_type, req_data in path_data.items():
                if 'x-tests' in req_data:
                    print("tests already found, skipping") # TODO: put this in a logfile
                    continue
                api_schema['paths'][path_name][req_type]['x-tests'] = []
                
                path_tokens = []
                query_tokens = []
                self.resolved_tests = []
                if 'parameters' in req_data:
                    for parameter in req_data['parameters']:
                        token = (parameter['name'], parameter['schema']['type'])
                        if parameter['in'] == 'path':
                            path_tokens.append(token)
                        elif parameter['in'] == 'query':
                            query_tokens.append(token)
                        # TODO: any more of these?

                component_schema = {}
                if 'requestBody' in req_data:
                    component_schema_name = req_data['requestBody']['content']['application/json']['schema']['$ref'].split('/')[-1]
                    component_schema = api_schema['components']['schemas'][component_schema_name]['properties']

                resolve_test_with_strategies = given(st.data())(self.resolve_test)
                resolve_test_with_strategies(self, path_name, path_tokens, query_tokens, component_schema)

                # Save test to schema
                api_schema['paths'][path_name][req_type]['x-tests'] = self.resolved_tests

        return api_schema

    # Replace tokens with generated values
    @staticmethod
    @settings(max_examples=100)
    def resolve_test(
        self,
        path_name: str,
        path_tokens: [(str, str)],
        query_tokens: [(str, str)],
        component_schema: {},
        data):

        # Path tokens
        for token_name, token_type in path_tokens:
            replacement = data.draw(PARAM_TYPE_MAPPING[token_type], label = token_name)
            path_name = path_name.replace("{" + token_name + "}", str(replacement))

        # Query tokens
        separator = '?'
        for token_name, token_type in query_tokens:
            token_value = data.draw(PARAM_TYPE_MAPPING[token_type], label = token_name)
            path_name = path_name + separator + token_name + '=' + str(token_value)
            separator = '&'

        # Component data
        test_data = {}
        for component_name, component_data in component_schema.items():
            test_data[component_name] = data.draw(PARAM_TYPE_MAPPING[component_data['type']], label = component_name)

        self.resolved_tests.append({'path': path_name, 'data': test_data})