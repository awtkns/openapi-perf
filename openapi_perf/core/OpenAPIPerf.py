from urllib.parse import urljoin

# import hypothesis
import requests

REQ_TYPE_MAPPING = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete
}


class OpenAPIPerf:
    schema = {}
    endpoint_url = ''
    schema_url = ''

    def __init__(self, endpoint_url='', schema_path=''):
        if not endpoint_url.startswith('http'):
            endpoint_url = "http://" + endpoint_url

        self.endpoint_url = endpoint_url
        self.schema_url = urljoin(endpoint_url, schema_path)

        try:
            self.schema = self.get_api_schema(self.schema_url)
        except AssertionError:
            if self.schema_url.endswith('.json'):
                self.schema_url.removesuffix('.json')
            else:
                self.schema_url = self.schema_url + '.json'

            self.schema = self.get_api_schema(self.schema_url)

    @staticmethod
    def get_api_schema(url) -> dict:
        res = requests.get(url)
        schema = res.json

        assert res.status_code == 200, f"Could bot reach schema endpoint {url}"
        assert schema, "No Schema was Found"

        return schema

    def run(self):
        responseData = {}

        for pathName, pathData in self.schema['paths'].items():
            for reqType, reqData in pathData.items():
                execute = REQ_TYPE_MAPPING[reqType]
                response = execute(self.endpoint_url + pathName)
                responseData[pathName + ': ' + reqType] = response

        return responseData
