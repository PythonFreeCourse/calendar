OK_STATUS_CODE = 200
DATA_IN_SHORTCUTS_PAGE = b"General Shortcuts"


class TestKeyboardShortcuts:
    URL = "/keyboard_shortcuts"

    def test_get_page(self, client):
        res = client.get(self.URL)
        assert res.ok

    def test_get_keyboard_shortcuts_page(self, client):
        res = client.get(self.URL)
        assert DATA_IN_SHORTCUTS_PAGE in res.content
