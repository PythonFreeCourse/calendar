from pathlib import Path

import pytest

from app.internal import languages


class TestLanguage:
    # Empty, invalid, or valid, but unsupported non-'he' language codes,
    # are set to the default language setting at config.WEBSITE_LANGUAGE,
    # which is currently set to 'en' (English).
    LANGUAGE_TESTS = [
        ('en', 'test python translation', 'Profile', True),
        ('he', 'בדיקת תרגום בפייתון', 'פרופיל', True),
        (None, 'test python translation', 'Profile', False),
        ('', 'test python translation', 'Profile', False),
        ('de', 'test python translation', 'Profile', False),
        (["en"], 'test python translation', 'Profile', False),
        (3, 'test python translation', 'Profile', False),
    ]

    NUMBER_OF_LANGUAGES = 2

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, __, is_valid",
                             LANGUAGE_TESTS)
    def test_gettext_python(client, language_code, translation, __, is_valid):
        languages.set_ui_language(language_code)
        gettext_translation = _("test python translation")  # noqa F821
        assert ((is_valid and gettext_translation == translation)
                or (not is_valid and gettext_translation == translation))

    @staticmethod
    @pytest.mark.parametrize("language_code, __, translation, is_valid",
                             LANGUAGE_TESTS)
    def test_gettext_html(client, language_code, __, translation, is_valid):
        languages.set_ui_language(language_code)
        text = client.get("/").text
        assert ((is_valid and translation in text)
                or (not is_valid and translation in text))

    @staticmethod
    def test_get_supported_languages():
        number_of_languages = len(list(languages._get_supported_languages()))
        assert number_of_languages == TestLanguage.NUMBER_OF_LANGUAGES

    @staticmethod
    def test_get_language_directory():
        pytest.MonkeyPatch().setattr(Path, 'is_dir', lambda x: True)
        assert languages._get_language_directory()

    @staticmethod
    def test_get_display_language():
        # TODO: Waiting for user registration.
        #  Test: no user, user not logged in and user with non-english set.
        pass
