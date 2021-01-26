import pytest

from app.internal import languages


class TestLanguage:
    PYTHON_TESTS = [
        (None, 'test python translation', False),
        ('', 'test python translation', False),
        ('en', 'test python translation', True),
        ('he', 'בדיקת תרגום בפייתון', True),
        ('de', 'test python translation', False),  # Defaults to English.
        (["en"], 'test python translation', False),
        (3, 'test python translation', False),
    ]

    HTML_TESTS = [
        (None, 'Profile', False),
        ('', 'Profile', False),
        ('en', 'Profile', True),
        ('he', 'פרופיל', True),
        ('de', 'Profile', False),  # Defaults to English translation.
        (["en"], 'Profile', False),
        (3, 'Profile', False),
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
        languages.set_ui_language(language_code)
        gettext_translation = _("test python translation")  # noqa F821
        assert ((is_valid and gettext_translation == translation)
                or (not is_valid and gettext_translation == translation))

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             HTML_TESTS)
    def test_gettext_html(client, language_code, translation, is_valid):
        languages.set_ui_language(language_code)
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
