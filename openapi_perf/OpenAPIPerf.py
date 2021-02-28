import hypothesis
import requests

class OpenAPIPerf:
    REQ_TYPE_MAPPING = {
        "get": requests.get,
        "post": requests.post,
        "put": requests.put,
        "delete": requests.delete
    }

    schema = {}
    endpoint_url = ''

    def __init__(self, endpoint_url='', schema_path=''):
        res = requests.get(endpoint_url + schema_path)
        self.schema = res.json()
        self.endpoint_url = endpoint_url

    def run(self):
        responseData = {}

        for pathName, pathData in self.schema['paths'].items():
            for reqType, reqData in pathData.items():
                execute = self.REQ_TYPE_MAPPING[reqType]
                response = execute(self.endpoint_url + pathName)
                responseData[pathName + ': ' + reqType] = response
                
        return responseData