from fastapi import Request

from app.internal import utilities
from app.main import app


class TestUtilities:

    @staticmethod
    def test_get_template_response():
        request = Request({
            "type": "http",
            "router": app.router,
            "headers": [(b'host', b'testserver'),
                        (b'user-agent', b'testclient'),
                        (b'accept-encoding', b'gzip, deflate'),
                        (b'accept', b'*/*'), (b'connection', b'keep-alive')],
        })

        assert utilities.get_template_response("home.html", request)
