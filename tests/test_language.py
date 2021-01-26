import pytest

from app.internal import languages


class TestLanguage:
    PYTHON_TESTS = [
        ('en', 'test', True),
        ('he', 'בדיקה', True),
        ('de', 'test', False),  # Defaults to English translation.
    ]

    HTML_TESTS = [
        ('en', 'Profile', True),
        ('he', 'פרופיל', True),
        ('de', 'Profile', False),  # Defaults to English translation.
    ]

    NUMBER_OF_LANGUAGES = 2

    @staticmethod
    def test_setup_ui_language():
        languages.setup_ui_language()
        assert True

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             PYTHON_TESTS)
    def test_gettext_python(client, language_code, translation, is_valid):
        languages.change_ui_language(language_code)
        gettext_translation = _("test")  # noqa F821
        assert ((is_valid and gettext_translation == translation)
                or (not is_valid and gettext_translation == translation))

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             HTML_TESTS)
    def test_gettext_html(client, language_code, translation, is_valid):
        languages.change_ui_language(language_code)
        text = client.get("/").text
        assert ((is_valid and translation in text)
                or (not is_valid and translation in text))

    @staticmethod
    def test_get_supported_languages():
        number_of_languages = len(languages._get_supported_languages())
        assert number_of_languages == TestLanguage.NUMBER_OF_LANGUAGES

    @staticmethod
    def test_get_display_language():
        # TODO: Waiting for user registration.
        #  Test: no user, user not logged in and user with non-english set.
        pass
