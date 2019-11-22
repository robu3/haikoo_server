class MockResponse:
    def __init__(self, status_code=200, headers={}):
        self.status_code = status_code
        self.headers = headers
