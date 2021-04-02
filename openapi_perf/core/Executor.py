from urllib.parse import urljoin
import requests
import time

REQ_TYPE_MAPPING = {
    "get": requests.get,
    "post": requests.post,
    "put": requests.put,
    "delete": requests.delete,
}

def execute(test_schema: {}, api_schema: {}):
    endpoint_url = test_schema["endpoint_url"]
    response_data = []

    # TODO: multi-thread this
    for path_name, path_data in api_schema["paths"].items():
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