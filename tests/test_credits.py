class TestCredits:
    CREDITS_OPENING = b"Say hello to our developers"

    @staticmethod
    def test_get_credits_ok_request(client):
        response = client.get("/credits")
        assert response.ok
        assert TestCredits.CREDITS_OPENING in response.content
