class TestHome:
    URL = "/"

    @staticmethod
    def test_get_page(client):
        response = client.get(TestHome.URL)
        assert response.ok
