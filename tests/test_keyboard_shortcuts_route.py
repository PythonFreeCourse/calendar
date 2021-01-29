OK_STATUS_CODE = 200


class TestKeyboardShortcuts:
    URL = "/keyboard_shortcuts"

    def test_get_page(self, client):
        res = client.get(self.URL)
        assert res.status_code == OK_STATUS_CODE
