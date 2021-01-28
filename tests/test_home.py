from fastapi import status


class TestHome:
    URL = "/"

    def test_get_page(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == status.HTTP_200_OK
