from fastapi import status

import pytest


class TestHome:
    URL = "/"

    @pytest.mark.home
    def test_get_page(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
