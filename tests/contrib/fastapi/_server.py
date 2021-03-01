"""
Adapted from https://github.com/encode/uvicorn/issues/742
"""

import contextlib
import time
import threading
import uvicorn


class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    def __init__(self, app, host: str = '127.0.0.1', port: int = 5000):
        config = uvicorn.Config(app, host, port)
        super().__init__(config=config)

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
