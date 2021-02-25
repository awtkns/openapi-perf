import pytest
import uvicorn

from tests.contrib import implementations


@pytest.fixture(params=implementations, autouse=True, scope='session')
def api(request):
    with request.param.run_in_thread():
        yield
