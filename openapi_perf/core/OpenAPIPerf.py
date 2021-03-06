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
    resolvedPathName = ''

    def __init__(self, endpoint_url='', schema_path='', generate=True):
        if not endpoint_url.startswith('http'):
            endpoint_url = "http://" + endpoint_url
        self.endpoint_url = endpoint_url

        schema_url = urljoin(endpoint_url, schema_path)

        try:
            self.schema = self.get_api_schema(schema_url)
        except AssertionError:
            if schema_url.endswith('.json'):
                schema_url.removesuffix('.json')
            else:
                schema_url = schema_url + '.json'

            self.schema = self.get_api_schema(schema_url)

        if generate: self.generateTests()

    @staticmethod
    def get_api_schema(url) -> dict:
        res = requests.get(url)
        schema = res.json()

        assert res.status_code == 200, f"Could not reach schema endpoint {url}"
        assert schema, "No Schema was Found"

        return schema

    # Generate the list of property-based tests
    def generateTests(self):
        def resolvePath(pathName, parameterName, parameterValue):
            self.resolvedPathName = pathName.replace("{" + parameterName + "}", str(parameterValue))

        for pathName, pathData in self.schema['paths'].items():
            for reqType, reqData in pathData.items():
                
                self.resolvedPathName = pathName
                if 'parameters' in reqData:
                    for parameter in reqData['parameters']:
                        if parameter['in'] == 'path':
                            resolvePathWithStrategy = given(PARAM_TYPE_MAPPING[parameter['schema']['type']]())(self.resolvePath)
                            resolvePathWithStrategy(self, pathName, parameter['name'])
                        
                        # TODO: support parameters which are not part of path

                self.schema['paths'][pathName][reqType]['x-tests'] = [{"path": self.resolvedPathName, "data": 0}]

    # Run tests and return results
    def run(self):

        responseData = []

        # TODO: multi-thread this
        for pathName, pathData in self.schema['paths'].items():
            for reqType, reqData in pathData.items():

                assert 'x-tests' in reqData, f'Test data not generated'
                for test in reqData['x-tests']:
                    print(test['path'])
                    execute = REQ_TYPE_MAPPING[reqType]
                    response = execute(urljoin(self.endpoint_url, test['path']))
                    responseData.append(response)

        return responseData

    # Replace token in path with a value
    @staticmethod
    def resolvePath(self, pathName, parameterName, parameterValue):
        self.resolvedPathName = pathName.replace("{" + parameterName + "}", str(parameterValue))
        
        
